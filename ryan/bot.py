import logging
import socket

import aiohttp
import arrow
from discord.ext import commands
from tortoise import Tortoise

from ryan import models
from ryan.database import Database

log = logging.getLogger(__name__)


async def init_tortoise() -> None:
    """
    Initialize Tortoise connection.

    This must be done from an async context. Generating schemas in 'safe' mode
    guards queries by 'IF NOT EXISTS', so this is ok to run everytime.

    Migrations must currently be handled manually.
    """
    log.info("Initializing Tortoise connection")
    await Tortoise.init(
        db_url="sqlite://ryan.db",
        modules={"models": [models.__name__]},
    )
    await Tortoise.generate_schemas(safe=True)


class Ryan(commands.Bot):

    start_time: arrow.Arrow
    database: Database

    def __init__(self, *args, **kwargs) -> None:
        """
        Prepare an aiohttp session for the bot to use.

        All args and kwargs propagate to super.
        """
        super().__init__(*args, **kwargs)
        self.http_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(resolver=aiohttp.AsyncResolver(), family=socket.AF_INET)
        )

    def add_cog(self, cog: commands.Cog) -> None:
        """
        Delegate to super, log successful loads.

        This reduces having to log in cog module setups.
        """
        super().add_cog(cog)
        log.info(f"Cog loaded: {cog.qualified_name}")

    async def start(self, *args, **kwargs) -> None:
        """
        Prepare Bot subclass.

        We establish a connection to the database here from an async context,
        then delegate to the base class.
        """
        self.start_time = arrow.now()
        self.database = await Database().open()

        await super().start(*args, **kwargs)

        log.info("Bot online")

    async def close(self) -> None:
        """Allow base class to close, then safely close database connection and http session."""
        await super().close()
        await self.database.close()
        await self.http_session.close()
