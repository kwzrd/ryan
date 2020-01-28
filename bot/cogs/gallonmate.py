import random
import logging

import discord
from discord.ext.commands import Bot, Cog

from bot.constants import Emoji, Channels, Users
from bot.utils import relay_message


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def is_gallonmate(user: discord.User) -> bool:
    return user.id == Users.gallonmate


class Gallonmate(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Listen for Gallonmate messages and evaluate whether they shall be galooned."""
        if (
            not is_gallonmate(message.author)
            or not isinstance(message.channel, discord.TextChannel)
        ):
            return

        roll = random.randint(0, 99)
        log.info(f"Roll {roll}")
        if roll == 0:
            target_channel = self.bot.get_channel(Channels.gallonmate_rolls)
            await message.add_reaction(Emoji.galooned)
            await relay_message(message, target_channel)


def setup(bot: Bot) -> None:
    """Load Gallonmate cog."""
    bot.add_cog(Gallonmate(bot))
    log.info("Gallonmate cog loaded")