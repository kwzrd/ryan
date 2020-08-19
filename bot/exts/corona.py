import logging
import typing as t

import aiohttp
from discord.ext import commands

from bot.bot import Ryan

URL_API = "https://api.covid19api.com/summary"
URL_FLAGS = "https://www.countryflags.io/{code}/flat/64.png"

log = logging.getLogger(__name__)


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
