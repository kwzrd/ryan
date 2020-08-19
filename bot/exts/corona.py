import logging

from discord.ext import commands

from bot.bot import Ryan

URL_API = "https://api.covid19api.com/summary"
URL_FLAGS = "https://www.countryflags.io/{code}/flat/64.png"

log = logging.getLogger(__name__)


class Corona(commands.Cog):
    """Provide basic per-country coronavirus statistics."""

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot


def setup(bot: Ryan) -> None:
    """Load Corona cog."""
    bot.add_cog(Corona(bot))
