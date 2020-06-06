import contextlib
import difflib
import logging
import typing as t

import aiohttp
import arrow
import discord
import pycountry
from discord.ext import commands, tasks

from bot.bot import Ryan
from bot.constants import Emoji

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

better_keys = {
    "todaycases": "cases today",
    "todaydeaths": "deaths today",
    "casesperonemillion": "cases per million",
    "deathsperonemillion": "deaths per million",
    "totaltests": "total tests",
    "testsperonemillion": "tests per million",
}


async def cute_dict(dct: t.Dict[str, t.Union[str, int]]) -> str:
    """Make `dct` readable in Discord's markdown."""
    lines = list()

    for key, val in dct.items():
        key = f"**{better_keys.get(key.casefold(), key).capitalize()}**"
        with contextlib.suppress(ValueError, TypeError):
            val = f"{int(val):,}"
        lines.append(f"{key}: {val}")

    return "\n".join(lines)


class Corona(commands.Cog):
    """Wrapper for coronavirus API.

    See: https://github.com/javieraviles/covidapi
    """

    INTERVAL = 60  # Once an hour

    url_all = "https://coronavirus-19-api.herokuapp.com/all"
    url_countries = "https://coronavirus-19-api.herokuapp.com/countries"

    url_flags = "https://www.countryflags.io/{code}/flat/64.png"

    all: t.Dict[str, t.Any] = {}
    countries: t.Dict[str, t.Dict[str, t.Any]] = {}

    last_refresh: t.Optional[arrow.Arrow] = None

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot
        self.refresh_task.start()

    async def get(self, url: str) -> t.Any:
        """Make a GET request to `url` and return response parsed json."""
        logger.info(f"Get: {url}")
        try:
            async with self.bot.http_session.get(url) as resp:
                return await resp.json()
        except aiohttp.ClientError as exc:
            logger.error(f"Get failed: {exc}")
            return None

    async def refresh(self) -> None:
        """Refresh cache & counts."""
        logger.info("Refreshing cache")
        self.all = await self.get(self.url_all) or {}

        country_list = await self.get(self.url_countries) or []
        self.countries = {
            record["country"].casefold(): record
            for record in country_list
        }

        self.last_refresh = arrow.utcnow()

    @tasks.loop(minutes=INTERVAL)
    async def refresh_task(self) -> None:
        """Periodically call refresh."""
        await self.refresh()

    @commands.group(name="corona", aliases=["covid"], invoke_without_command=True)
    async def corona_cmd(self, ctx: commands.Context, *, country: t.Optional[str] = None) -> None:
        """Give cached information about the covid."""
        if country is None:
            response = discord.Embed(
                description=await cute_dict(self.all) or "Cache empty",
                colour=discord.Colour.green(),
            )
            response.set_author(name="General stats")

        else:
            country = country.casefold()
            record = self.countries.get(country)

            if record is not None:
                try:
                    country_code = pycountry.countries.search_fuzzy(country)[0].alpha_2
                except LookupError:
                    country_code = None

                name = country_code or country.title()
                flag = self.url_flags.format(code=country_code) if country_code is not None else ""
                desc = await cute_dict(record) or "Cache empty"
                colour = discord.Colour.green()

            else:
                guess = difflib.get_close_matches(country, self.countries.keys(), n=1)
                if guess:
                    closest_match = str(guess[0]).title()
                else:
                    closest_match = 'none found'

                name = "No such country found"
                flag = ""
                desc = f"Closest match in cache: {closest_match}"
                colour = discord.Colour.red()

            response = discord.Embed(description=desc, colour=colour)
            response.set_author(name=name, icon_url=flag)

        if self.last_refresh is not None:
            response.set_footer(text=f"Last refresh {self.last_refresh.humanize(arrow.utcnow())}")

        await ctx.send(embed=response)

    @corona_cmd.command(name="status")
    async def corona_status(self, ctx: commands.Context) -> None:
        response = discord.Embed(
            description=(
                f"There are currently **{len(self.countries)}** countries in the cache.\n"
                f"Last refresh has taken place {self.last_refresh.humanize()}.\n"
                f"Cache will refresh automatically every {self.INTERVAL} minutes."
            ),
            color=discord.Colour.green() if self.countries else discord.Colour.red()
        )
        await ctx.send(embed=response)

    @commands.is_owner()
    @corona_cmd.command(name="refresh")
    async def corona_refresh(self, ctx: commands.Context) -> None:
        await self.refresh()
        await ctx.send(
            embed=discord.Embed(description=f"Refresh completed {Emoji.ok_hand}", color=discord.Colour.green())
        )


def setup(bot: Ryan) -> None:
    """Load Corona cog."""
    bot.add_cog(Corona(bot))
