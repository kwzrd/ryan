import logging
import typing as t

import discord
from discord.ext import commands

from ryan.bot import Ryan
from ryan.constants import Users

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


def setup(bot: Ryan) -> None:
    """Load Gallonmate cog."""
    bot.add_cog(Galoon(bot))
