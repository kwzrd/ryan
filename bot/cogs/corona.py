import logging

from discord.ext import commands

from bot.bot import Bot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Corona(commands.Cog):
    """Wrapper for coronavirus API.

    See: https://github.com/javieraviles/covidapi
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot


def setup(bot: Bot) -> None:
    """Load Corona cog."""
    bot.add_cog(Corona(bot))
    logger.info("Corona cog loaded")
