import subprocess
from typing import List

import arrow
import discord
from discord.ext import commands

from bot.bot import Ryan
from bot.constants import Client


def run_git(args: List[str]) -> str:
    """Run a git command specified by `args`, capture its stdout output and return as string."""
    return subprocess.run(["git"] + args, capture_output=True, text=True).stdout.strip()


latest_tag = run_git(["describe", "--tags"])
tag_author = run_git(["show", latest_tag, "-s", "--format=%h:%an"])
tag_tstamp = run_git(["show", latest_tag, "-s", "--format=%ci"]).split()[0]  # Date only

bot = Ryan(command_prefix="?", activity=discord.Game(f"{latest_tag}"), help_command=None)

# Instantiate all extensions
bot.load_extension("bot.exts.corona")
bot.load_extension("bot.exts.error_handler")
bot.load_extension("bot.exts.execute")
bot.load_extension("bot.exts.gallonmate")
bot.load_extension("bot.exts.seasons")


@bot.command(name="help")
async def custom_help(ctx: commands.Context) -> None:
    """Custom help command with basic information."""
    help_embed = discord.Embed(
        description=f"Revision:\n`{latest_tag}\n{tag_tstamp} ({tag_author})`",
        colour=discord.Colour.green(),
    )
    help_embed.set_author(name="Ryan ~ real human bean", icon_url=bot.user.avatar_url)

    active_cogs = "\n".join(cog for cog in bot.cogs)
    help_embed.add_field(name="Active extensions:", value=active_cogs, inline=False)

    help_embed.set_footer(text=f"Awakened {bot.start_time.humanize(arrow.now())}")
    await ctx.send(embed=help_embed)


bot.run(Client.token)
