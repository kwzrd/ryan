import logging
from datetime import datetime
from typing import Optional

from discord.ext import commands

from bot.database import Database

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Bot(commands.Bot):

    start_time: datetime
    database: Database

    season: Optional[str]

    async def start(self, *args, **kwargs) -> None:
        self.start_time = datetime.now()
        self.database = await Database().open()

        await super().start(*args, **kwargs)

        logger.info("Bot online")

    async def close(self) -> None:
        await super().close()
        await self.database.close()
