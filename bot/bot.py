import logging
from datetime import datetime

from discord.ext import commands

from bot.database import Database

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Bot(commands.Bot):

    start_time: datetime
    database: Database

    async def start(self, *args, **kwargs) -> None:
        """Prepare Bot subclass.

        We establish a connection to the database here from an async context,
        then delegate to the base class.
        """
        self.start_time = datetime.now()
        self.database = await Database().open()

        await super().start(*args, **kwargs)

        logger.info("Bot online")

    async def close(self) -> None:
        """Allow base class to close, then safely close database connection."""
        await super().close()
        await self.database.close()
