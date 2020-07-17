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
tag_tstamp = run_git(["log", "-1", "--format=%ci", latest_tag]).split()[0]  # Date only

bot = Ryan(command_prefix="?", activity=discord.Game(f"version {latest_tag}"), help_command=None)

# Instantiate all extensions
bot.load_extension("bot.exts.corona")
bot.load_extension("bot.exts.error_handler")
bot.load_extension("bot.exts.execute")
bot.load_extension("bot.exts.extensions")
bot.load_extension("bot.exts.gallonmate")
bot.load_extension("bot.exts.seasons")


@bot.command(name="help")
async def custom_help(ctx: commands.Context) -> None:
    """Custom help command with basic information."""
    help_embed = discord.Embed(colour=discord.Colour.green())

    # Field: bot name & icon
    help_embed.set_author(name="Ryan ~ real human bean", icon_url=bot.user.avatar_url)

    # Field: revision
    help_embed.add_field(name="Revision:", value=f"`{latest_tag} ({tag_tstamp})`")

    # Field: active extensions
    active_cogs = "\n".join(cog for cog in bot.cogs)
    help_embed.add_field(name="Active extensions:", value=active_cogs, inline=False)

    # Field: footer
    help_embed.set_footer(text=f"Awakened {bot.start_time.humanize(arrow.now())}")

    await ctx.send(embed=help_embed)


bot.run(Client.token)
