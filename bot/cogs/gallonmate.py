import logging
import random

import discord
from discord.ext import commands

from bot.bot import Bot
from bot.constants import Channels, Emoji, Users
from bot.utils import relay_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

title_success = (
    "Good point",
    "Great moves Ethan",
    "Keep it up",
)

title_error = (
    "Galooned again",
    "Put on full blast",
)


def msg_success(message: str) -> discord.Embed():
    """Create a success embed with `message`."""
    return discord.Embed(
        title=random.choice(title_success),
        description=message,
        colour=discord.Colour.green(),
    )


def msg_error(message: str) -> discord.Embed():
    """Create an error embed with `message`."""
    return discord.Embed(
        title=random.choice(title_error),
        description=message,
        colour=discord.Colour.red(),
    )


def is_gallonmate(user: discord.User) -> bool:
    """Check whether `user` is Gallonmate."""
    return user.id == Users.gallonmate


class Gallonmate(commands.Cog):
    """Cog with Gallonmate-specific functionality."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for Gallonmate messages and evaluate whether they shall be galooned."""
        if (
            not is_gallonmate(message.author)
            or not isinstance(message.channel, discord.TextChannel)
        ):
            return

        roll = random.randint(0, 99)
        logger.info(f"Roll {roll}")
        if roll == 0:
            target_channel = self.bot.get_channel(Channels.gallonmate_rolls)
            await message.add_reaction(Emoji.galooned)
            await relay_message(message, target_channel)

    @commands.group()
    async def gallonmate(self, ctx: commands.Context) -> None:
        """Parent command for Gallonmate-specific functionality."""
        if not ctx.invoked_subcommand:
            await self.help(ctx)

    @gallonmate.command()
    async def add_nickname(self, ctx: commands.Context, *, value: str) -> None:
        """Register new nickname."""
        ...

    @gallonmate.command()
    async def apply_nickname(self, ctx: commands.Context) -> None:
        """Draw a random nickname and apply it to Gallonmate."""
        ...

    @gallonmate.command()
    async def remove_nickname(self, ctx: commands.Context, *, value: str) -> None:
        """Remove specific nickname."""
        ...

    @gallonmate.command()
    async def list_nicknames(self, ctx: commands.Context) -> None:
        """List all available nicknames."""
        ...

    @gallonmate.command()
    async def clear_nicknames(self, ctx: commands.Context) -> None:
        """Remove all nicknames."""
        ...

    @gallonmate.command()
    async def help(self, ctx: commands.Context) -> None:
        """Provide an embed with module's commands."""
        help_embed = discord.Embed(
            title="Gallonmate",
            description="Available commands in Gallonmate group",
        )

        for cmd in self.gallonmate.commands:
            help_embed.add_field(name=cmd.name, value=cmd.brief, inline=False)

        await ctx.send(embed=help_embed)


def setup(bot: Bot) -> None:
    """Load Gallonmate cog."""
    bot.add_cog(Gallonmate(bot))
    logger.info("Gallonmate cog loaded")
