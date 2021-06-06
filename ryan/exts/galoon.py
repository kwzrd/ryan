import logging
import random
import typing as t

import discord
from discord.ext import commands

from ryan.bot import Ryan
from ryan.config import Channels, Emoji, Users
from ryan.utils import relay_message

USERS = {Users.gallonmate}  # Users which can be galooned

log = logging.getLogger(__name__)


def galoonable(user: t.Union[discord.Member, discord.User]) -> bool:
    """True if `user` can be galooned."""
    return user.id in USERS


class Galoon(commands.Cog):
    """Galoon rolls."""

    def __init__(self, bot: Ryan) -> None:
        """Initialize cog."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Galoon roll in-guild messages from `USERS`.

        If the message was sent in a guild, by a `galoonable` user, we roll.
        On successful rolls, the message receives a reaction and gets archived.
        """
        if not isinstance(message.channel, discord.TextChannel):
            return

        if not galoonable(message.author):
            return

        if random.randint(0, 99) != 0:
            return

        target_channel = self.bot.get_channel(Channels.gallonmate_rolls)
        await message.add_reaction(Emoji.galooned)
        await relay_message(message, target_channel)


def setup(bot: Ryan) -> None:
    """Load Gallonmate cog."""
    bot.add_cog(Galoon(bot))
