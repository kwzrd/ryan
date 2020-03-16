import subprocess
from datetime import datetime
from typing import List

import discord
from discord.ext import commands

from bot.bot import Bot
from bot.constants import Client, Users


def run_git(args: List[str]) -> str:
    """Run a git command specified by `args`, capture its stdout output and return as string."""
    return subprocess.run(["git"] + args, capture_output=True, text=True).stdout.strip()


commit = ["describe", "--always"]
branch = ["rev-parse", "--abbrev-ref", "HEAD"]
tstamp = ["log", "-1", "--format=%cd"]
dstamp = ["log", "-1", "--format=%as"]

vc_info = f"HEAD: {run_git(commit)} ({run_git(branch)})\n{run_git(tstamp)}"
activity = discord.Game(f"{run_git(commit)} ({run_git(dstamp)})")

bot = Bot(command_prefix="?", activity=activity)

bot.load_extension("bot.cogs.corona")
bot.load_extension("bot.cogs.gallonmate")
bot.load_extension("bot.cogs.seasons")

bot.remove_command("help")


@bot.command(name="help")
async def custom_help(ctx: commands.Context) -> None:
    """Custom help command with basic information."""
    help_embed = discord.Embed(
        title="I am Ryan",
        description="Real human bean",
        colour=discord.Colour.green(),
    )
    help_embed.set_thumbnail(url=bot.user.avatar_url)

    master_mention = bot.get_user(Users.kwzrd).mention
    help_embed.add_field(name="master", value=master_mention, inline=False)

    active_cogs = "\n".join(cog for cog in bot.cogs)
    help_embed.add_field(name="active modules", value=active_cogs, inline=False)

    help_embed.add_field(name="uptime", value=f"{datetime.now() - bot.start_time}", inline=False)

    help_embed.add_field(name="version control", value=vc_info, inline=False)

    await ctx.send(embed=help_embed)


bot.run(Client.token)
