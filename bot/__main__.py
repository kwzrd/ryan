import logging
import sys

from bot.bot import Bot
from bot.config import Config

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

bot = Bot(command_prefix="?")

bot.load_extension("bot.cogs.gallonmate")
bot.load_extension("bot.cogs.seasons")

bot.remove_command("help")

bot.run(Config.token)
