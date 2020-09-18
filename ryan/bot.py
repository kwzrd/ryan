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
    """
    Custom bot class.

    This holds attributes globally accessible to all cogs.
    """

    http_session: aiohttp.ClientSession
    database: Database
    start_time: arrow.Arrow

    def add_cog(self, cog: commands.Cog) -> None:
        """Log cog name & delegate to super."""
        log.info(f"Loading cog: {cog.qualified_name}")
        super().add_cog(cog)

    async def start(self, *args, **kwargs) -> None:
        """
        Initialize from an async context.

        To ensure that the event loop is ready, we delay setting async attributes
        until after this method is called.
        """
        connector = aiohttp.TCPConnector(resolver=aiohttp.AsyncResolver(), family=socket.AF_INET)
        self.http_session = aiohttp.ClientSession(connector=connector)

        self.database = await Database().open()
        self.start_time = arrow.now()

        await super().start(*args, **kwargs)

    async def close(self) -> None:
        """
        Let parent close & clean up own connections.

        This handles graceful cleanup that should be done asynchronously.
        """
        await super().close()
        await self.database.close()
        await self.http_session.close()
