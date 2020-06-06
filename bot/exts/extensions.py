import logging

from discord.ext import commands

from bot.bot import Ryan

logger = logging.getLogger(__name__)


class Extensions(commands.Cog):
    """Allows extension management at runtime, e.g. live reloading."""

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot


def setup(bot: Ryan) -> None:
    """Load the Extensions cog."""
    bot.add_cog(Extensions(bot))
