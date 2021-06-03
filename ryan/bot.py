import logging
import socket

import aiohttp
import arrow
from discord.ext import commands

log = logging.getLogger(__name__)


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
        self.start_time = arrow.utcnow()

        connector = aiohttp.TCPConnector(resolver=aiohttp.AsyncResolver(), family=socket.AF_INET)
        self.http_session = aiohttp.ClientSession(connector=connector)

        log.info("Ryan ready, connecting to Discord")
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        """
        Let parent close & clean up own connections.

        This handles graceful cleanup that should be done asynchronously.
        """
        await super().close()

        log.info("Closing HTTP session")
        await self.http_session.close()
