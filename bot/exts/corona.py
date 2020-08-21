import logging
import typing as t

import aiohttp
from discord.ext import commands

from bot.bot import Ryan

URL_API = "https://api.covid19api.com/summary"
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


class Corona(commands.Cog):
    """Provide basic per-country coronavirus statistics."""

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot

    async def _pull_data(self) -> t.Optional[t.Dict[str, t.Any]]:
        """
        Poll coronavirus API for fresh information.

        Uses the bots internal aiohttp session. Returns None if the request fails,
        or if the response JSON fails to parse.
        """
        log.debug("Polling coronavirus API")
        try:
            async with self.bot.http_session.get(URL_API) as resp:
                log.debug(f"Response status: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            log.exception("Failed to acquire data from API", exc_info=err)


def setup(bot: Ryan) -> None:
    """Load Corona cog."""
    bot.add_cog(Corona(bot))
