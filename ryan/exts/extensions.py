import logging
import types
import typing as t

from discord.ext import commands

from ryan.bot import Ryan
from ryan.config import Emoji, Users
from ryan.utils import msg_error, msg_success

log = logging.getLogger(__name__)


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

    @ext_group.command(name="list", aliases=["ls"])
    async def ext_list(self, ctx: commands.Context) -> None:
        """Show a list of all active extensions."""
        active_extensions: t.Mapping[str, types.ModuleType] = self.bot.extensions
        log.debug(f"Active extensions: {active_extensions}")

        if active_extensions:
            readable = "\n".join(f"{i} | {ext_name}" for i, ext_name in enumerate(active_extensions.keys()))
            response = f"Active extensions:\n"f"```{readable}```"
            await ctx.send(embed=msg_success(response))

        else:
            await ctx.send(embed=msg_error("No extensions found!"))

    @ext_group.command(name="reload", aliases=["r"])
    async def ext_reload(self, ctx: commands.Context, *, ext_name: str) -> None:
        """
        Attempt to reload extension named `ext_name`.

        This simply delegates to d.py provided utility method, so we do not need to worry
        about much - if anything goes wrong during the reload, d.py will automatically
        fallback on previous state, pretending that nothing happened.

        The bot will report the result in `ctx`.
        """
        log.debug(f"Attempting to reload extension: {ext_name}")
        try:
            self.bot.reload_extension(ext_name)
        except Exception as exc:
            log.debug(f"Reload failed: {exc}")
            response = msg_error(f"Reload failed! {exc} {Emoji.angry}")
        else:
            response = msg_success(f"Reloaded `{ext_name}` successfully {Emoji.ok_hand}")

        await ctx.send(embed=response)


def setup(bot: Ryan) -> None:
    """Load the Extensions cog."""
    bot.add_cog(Extensions(bot))
