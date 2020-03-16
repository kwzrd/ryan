import logging
import typing as t
from datetime import datetime

import aiohttp
from discord.ext import commands, tasks

from bot.bot import Bot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Corona(commands.Cog):
    """Wrapper for coronavirus API.

    See: https://github.com/javieraviles/covidapi
    """

    INTERVAL = 15

    url_all = "https://coronavirus-19-api.herokuapp.com/all"
    url_countries = "https://coronavirus-19-api.herokuapp.com/countries"

    all: t.Dict[str, t.Any]
    countries: t.Dict[str, t.Dict[str, t.Any]]

    last_refresh: t.Optional[datetime]

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.refresh.start()

    async def get(self, url: str) -> t.Any:
        """Make a GET request to `url` and return response parsed json."""
        logger.info(f"Get: {url}")
        try:
            async with self.bot.http_session.get(url) as resp:
                return await resp.json()
        except aiohttp.ClientError as exc:
            logger.error(f"Get failed: {exc}")
            return None

    @tasks.loop(minutes=INTERVAL)
    async def refresh(self) -> None:
        """Periodically refresh & cache counts."""
        logger.info(f"Refreshing cache")
        self.all = await self.get(self.url_all) or {}

        country_list = await self.get(self.url_countries) or []
        self.countries = {
            record["country"].casefold(): record
            for record in country_list
        }

        self.last_refresh = datetime.now()


def setup(bot: Bot) -> None:
    """Load Corona cog."""
    bot.add_cog(Corona(bot))
    logger.info("Corona cog loaded")
