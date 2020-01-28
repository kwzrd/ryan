import logging
import sys
from datetime import datetime

import discord
from discord.ext import commands

from bot.config import Config
from bot.constants import Users

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

start_time = datetime.now()

bot = commands.Bot(command_prefix="?")

bot.load_extension("bot.cogs.gallonmate")
bot.load_extension("bot.cogs.seasons")

bot.remove_command("help")


@bot.command(name="help")
async def help_command(ctx: commands.Context) -> None:
    """Custom help command with basic information."""
    help_embed = discord.Embed(
        title="i am ryan",
        description="a real human bean",
        colour=discord.Colour.green(),
    )
    help_embed.set_thumbnail(url=bot.user.avatar_url)

    master_mention = bot.get_user(Users.kwzrd).mention
    help_embed.add_field(name="master", value=master_mention, inline=False)

    active_cogs = "\n".join(cog for cog in bot.cogs)
    help_embed.add_field(name="active modules", value=active_cogs, inline=False)

    help_embed.add_field(name="awake since", value=str(start_time), inline=False)

    await ctx.send(embed=help_embed)


bot.run(Config.token)
