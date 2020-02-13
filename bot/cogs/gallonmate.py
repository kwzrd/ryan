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

    @commands.group(aliases=["gallon", "gallo", "gm"])
    async def gallonmate(self, ctx: commands.Context) -> None:
        """Parent command for Gallonmate-specific functionality."""
        if not ctx.invoked_subcommand:
            await self.help_command(ctx)

    @gallonmate.command(name="add")
    async def add_nickname(self, ctx: commands.Context, *, value: str) -> None:
        """Register new nickname."""
        author: int = ctx.author.id
        target: int = Users.gallonmate

        await self.bot.database.add_nickname(author, target, value)

        await ctx.send(embed=msg_success(f"Inserted {value}!"))

    @gallonmate.command(name="apply")
    async def apply_nickname(self, ctx: commands.Context) -> None:
        """Draw a random nickname and apply it to Gallonmate."""
        await ctx.send(embed=msg_error("Command not yet implemented!"))

    @gallonmate.command(name="remove")
    async def remove_nickname(self, ctx: commands.Context, *, value: str) -> None:
        """Remove specific nickname."""
        await self.bot.database.remove_nickname(value)

        await ctx.send(embed=msg_success(f"Removed {value}!"))

    @gallonmate.command(name="list")
    async def list_nicknames(self, ctx: commands.Context) -> None:
        """List all available nicknames."""
        names = await self.bot.database.get_nicknames()

        if names:
            response_embed = msg_success("\n".join(n for n in names))
        else:
            response_embed = msg_error("No nicknames available")

        await ctx.send(embed=response_embed)

    @gallonmate.command(name="clear")
    async def clear_nicknames(self, ctx: commands.Context) -> None:
        """Remove all nicknames."""
        await self.bot.database.truncate_nicknames()

        await ctx.send(embed=msg_success(f"Table truncated!"))

    @gallonmate.command(name="help")
    async def help_command(self, ctx: commands.Context) -> None:
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
