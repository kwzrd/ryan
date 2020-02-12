import logging
import random

import discord
from discord.ext import commands

from bot.constants import Channels, Emoji, Users
from bot.utils import relay_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def is_gallonmate(user: discord.User) -> bool:
    """Check whether `user` is Gallonmate."""
    return user.id == Users.gallonmate


class Gallonmate(commands.Cog):
    """Cog with Gallonmate-specific functionality."""

    def __init__(self, bot: commands.Bot) -> None:
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


def setup(bot: commands.Bot) -> None:
    """Load Gallonmate cog."""
    bot.add_cog(Gallonmate(bot))
    logger.info("Gallonmate cog loaded")
