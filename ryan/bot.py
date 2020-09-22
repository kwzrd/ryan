import logging
import socket

import aiohttp
import arrow
from discord.ext import commands
from tortoise import Tortoise

from ryan import models

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
        db_url="sqlite://ryan.database",
        modules={"models": [models.__name__]},
    )
    await Tortoise.generate_schemas(safe=True)


class Ryan(commands.Bot):
    """
    Custom bot class.

    This holds attributes globally accessible to all cogs.
    """

    http_session: aiohttp.ClientSession
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
        log.info("Initializing Ryan attributes from an async context")
        self.start_time = arrow.now()

        connector = aiohttp.TCPConnector(resolver=aiohttp.AsyncResolver(), family=socket.AF_INET)
        self.http_session = aiohttp.ClientSession(connector=connector)

        await init_tortoise()

        log.info("Ryan ready, connecting to Discord")
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        """
        Let parent close & clean up own connections.

        This handles graceful cleanup that should be done asynchronously.
        """
        await super().close()

        log.info("Closing HTTP session & Tortoise connections")
        await self.http_session.close()
        await Tortoise.close_connections()
