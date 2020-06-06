import logging

from discord.ext import commands

from bot.bot import Ryan

logger = logging.getLogger(__name__)


class Extensions(commands.Cog):
    """Allows extension management at runtime, e.g. live reloading."""

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot

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
