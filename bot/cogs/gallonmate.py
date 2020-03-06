import asyncio
import datetime
import logging
import random
import string
from typing import Optional

import discord
from discord.ext import commands

from bot.bot import Bot
from bot.constants import Channels, Emoji, Guilds, Users
from bot.utils import relay_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

title_success = (
    "Good point",
    "Great moves Ethan",
    "Keep it up",
    "Life is excellent!",
    "The daemon congratulates you",
)

title_error = (
    "Galooned again",
    "Put on full blast",
    "Reduced you to memes",
    "Get in the kiln",
    "Idk & dunno",
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


async def seconds_until_midnight() -> int:
    """Give the amount of seconds needed to wait until the next-up midnight.

    The exact `midnight` moment is actually delayed to 5 seconds after, in order
    to avoid potential race conditions due to imprecise sleep.
    """
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    midnight = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, second=5)

    return (midnight - now).seconds


async def get_help(group: commands.Group, failed_cmd: bool) -> discord.Embed:
    """Provide an embed with commands of `group`.

    If `failed_cmd` is True, the embed is coloured orange. Green otherwise.
    """
    help_embed = discord.Embed(
        title=f"{group.name}".capitalize(),
        description=f"Available arguments in {group.name} group",
        colour=discord.Color.orange() if failed_cmd else discord.Color.green(),
    )

    for cmd in group.commands:
        aliases = ', '.join(alias for alias in cmd.aliases)
        help_embed.add_field(name=f"{cmd.name} [{aliases or 'NA'}]", value=cmd.short_doc, inline=False)

    return help_embed


class SwitchException(Exception):
    """Custom exception raised during an attempted switch shall have specific handling."""
    ...


class Gallonmate(commands.Cog):
    """Cog with Gallonmate-specific functionality."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.announce = True
        self.switch_daemon = self.bot.loop.create_task(self.switch_daemon_func())

    async def switch_daemon_func(self) -> None:
        """Background task calling `switch_routine` once a day."""
        await self.bot.wait_until_ready()
        logger.info(f"Daemon started")

        while True:
            await asyncio.sleep(await seconds_until_midnight())

            try:
                new_name = await self.switch_routine()
            except SwitchException as switch_exc:
                logger.error(f"Daily switch failed: {switch_exc}")
            else:
                logger.info(f"Daily switch successful: {new_name}")

                if self.announce:
                    msg = f"Daily nickname switch for <@{Users.gallonmate}> complete!"

                    ann_channel = self.bot.get_channel(Channels.gallonmate_announce)
                    await ann_channel.send(embed=msg_success(msg))

    async def switch_routine(self) -> str:
        """Routine to attempt to switch Gallonmate nickname.

        If the method fails at any point, it will raise SwitchException with an informative
        message the can be displayed to the user.

        Internally draws available nicknames from the database. No available nicknames will
        result in a raise.

        On success, return the new nickname.
        """
        available_names = await self.bot.database.get_nicknames()

        if not available_names:
            raise SwitchException("No nicknames available")

        tree_society: discord.Guild = self.bot.get_guild(Guilds.tree_society)

        if tree_society is None:
            raise SwitchException(f"Could not find guild (id: {Guilds.tree_society})")

        gallon = tree_society.get_member(Users.gallonmate)

        if gallon is None:
            raise SwitchException(f"Could not find Gallonmate (id: {Users.gallonmate})")

        current_emoji = [char for char in gallon.display_name if char not in string.printable]
        new_name = random.choice(available_names)

        if current_emoji:
            lhs, rhs = random.sample(population=current_emoji, k=2)
            new_name = lhs + new_name + rhs

        try:
            await gallon.edit(nick=new_name)

        except discord.Forbidden:
            raise SwitchException(f"Missing permissions for name change (STATUS: 403)")

        except discord.HTTPException as e:
            raise SwitchException(f"Failed to change name to {new_name} (STATUS: {e.status}, {e.text})")

        else:
            return new_name

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Cog can only be used in Tree Society."""
        return ctx.guild.id == Guilds.tree_society or ctx.author.id == Users.kwzrd

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
            await ctx.send(embed=await get_help(self.gallonmate, failed_cmd=True))

    @gallonmate.group(aliases=["d"])
    async def daemon(self, ctx: commands.Context) -> None:
        """Command sub-group to control the Gallonmate daemon."""
        if not ctx.invoked_subcommand:
            await ctx.send(embed=await get_help(self.daemon, failed_cmd=True))

    @daemon.command(name="status", aliases=["state"])
    async def daemon_status(self, ctx: commands.Context) -> None:
        """Check whether the daemon is currently running."""
        if self.switch_daemon.done():
            report = msg_error("Daemon is inactive")
        else:
            t_remaining = await seconds_until_midnight()
            delta = datetime.timedelta(seconds=t_remaining)

            report = msg_success(f"Daemon is running, scheduled switch in: {t_remaining} (delta: {delta})")

        await ctx.send(embed=report)

    @daemon.command(name="kill", aliases=["k", "stop", "disable"])
    async def daemon_kill(self, ctx: commands.Context) -> None:
        """If the daemon is running, stop it."""
        if self.switch_daemon.done():
            await ctx.send(embed=msg_error("Daemon is not running!"))
            return

        self.switch_daemon.cancel()
        await ctx.send(embed=msg_success("Daemon has been stopped"))

    @daemon.command(name="start", aliases=["enable"])
    async def daemon_start(self, ctx: commands.Context) -> None:
        """If the daemon is inactive, start it."""
        if not self.switch_daemon.done():
            await ctx.send(embed=msg_error("Daemon is already running!"))
            return

        self.switch_daemon = self.bot.loop.create_task(self.switch_daemon_func())
        await ctx.send(embed=msg_success("Daemon has been started"))

    @daemon.command(name="help", aliases=["h"])
    async def daemon_help(self, ctx: commands.Context) -> None:
        """Give the help embed directly."""
        await ctx.send(embed=await get_help(self.daemon, failed_cmd=False))

    @gallonmate.command(name="add", aliases=["a"])
    async def add_nickname(self, ctx: commands.Context, *, value: Optional[str] = None) -> None:
        """Register new nickname."""
        if (
            not value
            or value in await self.bot.database.get_nicknames()
            or any(char not in string.printable for char in value)
        ):
            await ctx.send(embed=msg_error("Value either invalid or duplicate (already exists)"))
            return

        author: int = ctx.author.id
        target: int = Users.gallonmate

        await self.bot.database.add_nickname(author, target, value)

        await ctx.send(embed=msg_success(f"Inserted {value}!"))

    @gallonmate.command(name="switch", aliases=["s", "change", "apply"])
    async def switch_nickname(self, ctx: commands.Context) -> None:
        """Draw a random nickname and apply it to Gallonmate."""
        try:
            new_name = await self.switch_routine()

        except SwitchException as switch_exc:
            reason = str(switch_exc)
            await ctx.send(embed=msg_error(reason))

        else:
            await ctx.send(embed=msg_success(f"Gallonmate nickname changed: {new_name}"))

    @gallonmate.command(name="remove", aliases=["rm"])
    async def remove_nickname(self, ctx: commands.Context, *, value: Optional[str] = None) -> None:
        """Remove specific nickname."""
        if not value or value not in await self.bot.database.get_nicknames():
            await ctx.send(embed=msg_error("Value either invalid or not present in database"))
            return

        await self.bot.database.remove_nickname(value)

        await ctx.send(embed=msg_success(f"Removed {value}!"))

    @gallonmate.command(name="list", aliases=["ls"])
    async def list_nicknames(self, ctx: commands.Context) -> None:
        """List all available nicknames."""
        names = await self.bot.database.get_nicknames()

        if names:
            response_embed = msg_success("\n".join(n for n in names))
        else:
            response_embed = msg_error("No nicknames available")

        await ctx.send(embed=response_embed)

    @gallonmate.command(name="clear", aliases=["clr"])
    async def clear_nicknames(self, ctx: commands.Context) -> None:
        """Remove all nicknames."""
        await self.bot.database.truncate_nicknames()

        await ctx.send(embed=msg_success(f"Table truncated!"))

    @gallonmate.command(name="help", aliases=["h"])
    async def gallonmate_help(self, ctx: commands.Context) -> None:
        """Give the help embed directly."""
        await ctx.send(embed=await get_help(self.gallonmate, failed_cmd=False))


def setup(bot: Bot) -> None:
    """Load Gallonmate cog."""
    bot.add_cog(Gallonmate(bot))
    logger.info("Gallonmate cog loaded")
