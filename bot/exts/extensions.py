import logging

from discord.ext import commands

from bot.bot import Ryan
from bot.constants import Users

logger = logging.getLogger(__name__)


class Extensions(commands.Cog):
    """
    Allows extension management at runtime, e.g. live reloading.

    This is mostly useful during development, as it prevents API abuse when testing changes.
    """

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot

    def cog_check(self, ctx: commands.Context) -> bool:
        """Only bot owner is allowed to use this cog."""
        return ctx.author.id == Users.kwzrd

    @commands.group("extensions", aliases=["extension", "ext"])
    async def ext_group(self, ctx: commands.Context) -> None:
        """Entry point to the extension."""
        ...

    @ext_group.command(name="reload", aliases=["r"])
    async def ext_reload(self, ctx: commands.Context, *, ext_name: str) -> None:
        """Attempt to reload extension named `ext_name`."""
        ...


def setup(bot: Ryan) -> None:
    """Load the Extensions cog."""
    bot.add_cog(Extensions(bot))
