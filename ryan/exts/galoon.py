import logging

from discord.ext import commands

from ryan.bot import Ryan

log = logging.getLogger(__name__)


class Galoon(commands.Cog):

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot


def setup(bot: Ryan) -> None:
    """Load Gallonmate cog."""
    bot.add_cog(Galoon(bot))
