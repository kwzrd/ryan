import difflib
import logging
import typing as t
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands, tasks

from bot.bot import Ryan
from bot.constants import Emoji
from bot.utils import msg_error, msg_success

URL_API_HOME = "https://covid19api.com/"
URL_API_DATA = "https://api.covid19api.com/summary"

URL_FLAGS = "https://www.countryflags.io/{code}/flat/64.png"

Record = t.Dict[str, t.Any]  # A single country record returned from the API

log = logging.getLogger(__name__)


class Country:
    """
    Protocol for storing API-provided data for a single country.

    An instance is constructed from a `Record`. This primarily serves to validate the input
    data and to compute a few extra properties on top. Once an instance is created,
    the attributes become safer to work with.
    """

    def __init__(self, record: Record) -> None:
        """
        Construct an instance from a dictionary.

        This is entirely naive and will fail on API changes.
        """
        self.name = str(record["Country"])  # Regular name form
        self.slug = str(record["Slug"])  # Standardized name form (API specific, most likely)
        self.code = str(record["CountryCode"])  # Alpha-2 ISO country code

        self.confirmed = int(record["TotalConfirmed"])
        self.confirmed_new = int(record["NewConfirmed"])

        self.recovered = int(record["TotalRecovered"])
        self.recovered_new = int(record["NewRecovered"])

        self.deaths = int(record["TotalDeaths"])
        self.deaths_new = int(record["NewDeaths"])

    def flag_url(self) -> str:
        """Inject own `code` into the flag url template."""
        return URL_FLAGS.format(code=self.code)


class CountryMap:
    """Wrap a Country map & provide convenience methods for look-ups."""

    @staticmethod
    def normalize(name: str) -> str:
        """Normalize country `name` for look-up."""
        return name.lower().replace(" ", "")

    def __init__(self, countries: t.List[Country]) -> None:
        """Initiate internal mapper."""
        self.map: t.Dict[str, Country] = {
            self.normalize(country.name): country
            for country in countries
        }
        self.timestamp = datetime.utcnow()

    def __len__(self) -> int:
        """Amount of countries in the map."""
        return len(self.map)

    def lookup(self, name: str) -> t.Optional[Country]:
        """
        Lookup country by `name`.

        First, `name` is normalized and checked for membership in the map. If found,
        the result is returned directly. Otherwise, we attempt to find a close match
        in the map's keys. If this fails as well, None is returned.
        """
        normal_name = self.normalize(name)
        log.debug(f"Name '{name}' normalized into '{normal_name}'")

        if (country := self.map.get(normal_name)) is not None:
            return country

        try:
            match = difflib.get_close_matches(normal_name, possibilities=self.map, n=1)[0]
        except IndexError:
            log.debug(f"Found no match for '{normal_name}'")
        else:
            return self.map[match]


class Corona(commands.Cog):
    """Provide basic per-country coronavirus statistics."""

    def __init__(self, bot: Ryan) -> None:
        """Initialize attributes & start refresh task."""
        self.bot = bot
        self.country_map: t.Optional[CountryMap] = None  # Must be initialized from an async context

        self.refresh_task.start()

    def cog_unload(self) -> None:
        """Kill refresh task, if running."""
        self.refresh_task.stop()

    # region: API & state management

    async def _pull_data(self) -> t.Optional[Record]:
        """
        Poll coronavirus API for fresh information.

        Uses the bots internal aiohttp session. Returns None if the request fails,
        or if the response JSON fails to parse.
        """
        log.debug("Polling coronavirus API")
        try:
            async with self.bot.http_session.get(URL_API_DATA) as resp:
                log.debug(f"Response status: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            log.exception("Failed to acquire data from API", exc_info=err)

    async def _make_map(self) -> t.Optional[CountryMap]:
        """
        Initiate a country map instance.

        This loads the pulled data into Country instance. If an error occurs, None will
        be returned. Otherwise, a CountryMap instance is given.
        """
        if (data := await self._pull_data()) is None:
            log.error("Failed to acquire fresh data")
            return

        try:
            countries = [Country(record) for record in data["Countries"]]
        except Exception as parse_exc:
            log.error("API response failed to parse", exc_info=parse_exc)
            return
        else:
            log.info("All countries parsed & validated successfully")
            return CountryMap(countries)

    async def refresh(self) -> bool:
        """
        Try to pull new data & refresh internal state.

        If something goes wrong, returns False and rolls back to previous state.
        """
        if not (new_state := await self._make_map()):
            log.error("Something has gone wrong, new state will not be applied")
            return False

        log.info("New state acquired, replacing old state")
        self.country_map = new_state
        return True

    @tasks.loop(hours=1)
    async def refresh_task(self) -> None:
        """Periodically pull fresh data & refresh state."""
        log.debug("Performing periodic state refresh")
        await self.refresh()

    # endregion
    # region: command interface

    @commands.group(name="corona", invoke_without_command=True)
    async def cmd_group(self, ctx: commands.Context, *, name: t.Optional[str] = None) -> None:
        """If no subcommand was invoked, try to match `name` to a country."""
        if None in (name, self.country_map):
            await ctx.invoke(self.cmd_status)
            return

        if (country := self.country_map.lookup(name)) is None:
            await ctx.send(embed=msg_error(f"No such country found. {Emoji.frown}"))
            return

        description = (
            f"Confirmed: `{country.confirmed}` (today: `{country.confirmed_new}`)\n"
            f"Recovered: `{country.recovered}` (today: `{country.recovered_new}`)\n"
            f"Deaths: `{country.deaths}` (today: `{country.deaths_new}`)\n"
        )
        embed = discord.Embed(description=description, colour=discord.Color.green())
        embed.set_author(name=country.name, icon_url=country.flag_url())
        await ctx.send(embed=embed)

    @cmd_group.command(name="status", aliases=["info", "about"])
    async def cmd_status(self, ctx: commands.Context) -> None:
        """Show info about internal state."""
        if self.country_map is not None:
            first_line = f"There are currently `{len(self.country_map)}` countries in the cache."
            make_embed = msg_success
        else:
            first_line = "Cache is empty, check log for errors."
            make_embed = msg_error

        embed = make_embed(f"{first_line}\nData is pulled periodically from [COVID19API]({URL_API_HOME}).")
        await ctx.send(embed=embed)

    @cmd_group.command(name="refresh", aliases=["pull"])
    async def cmd_refresh(self, ctx: commands.Context) -> None:
        """Refresh internal state."""
        log.debug("Manually refreshing internal state")
        if await self.refresh():
            resp = msg_success(f"Refreshed successfully! {Emoji.ok_hand}")
        else:
            resp = msg_error(f"Something has gone wrong, check log for details. {Emoji.weary}")

        await ctx.send(embed=resp)

    # endregion


def setup(bot: Ryan) -> None:
    """Load Corona cog."""
    bot.add_cog(Corona(bot))
