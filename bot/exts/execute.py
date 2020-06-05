import logging

from discord.ext import commands

from bot.bot import Ryan

log = logging.getLogger(__name__)


class Execute(commands.Cog):
    """Support for code injection & evaluation at runtime."""

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot


def setup(bot: Ryan) -> None:
    """Load ErrorHandler cog."""
    bot.add_cog(Execute(bot))
