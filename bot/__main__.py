import logging
import sys

from discord.ext import commands

from bot.config import Config

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

bot = commands.Bot(command_prefix="?")

bot.load_extension("bot.cogs.gallonmate")
bot.load_extension("bot.cogs.seasons")

bot.run(Config.token)
