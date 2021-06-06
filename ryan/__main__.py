from os import environ

import arrow
import discord
from discord.ext import commands

from ryan.bot import Ryan
from ryan.config import App, Secrets

revision = environ.get("REVISION")

intents = discord.Intents.default()
intents.members = True

bot = Ryan(
    command_prefix=App.prefix,
    activity=discord.Game(f"version {revision}"),
    help_command=None,
    intents=intents,
)

# Instantiate all extensions
bot.load_extension("ryan.exts.corona")
bot.load_extension("ryan.exts.error_handler")
bot.load_extension("ryan.exts.execute")
bot.load_extension("ryan.exts.extensions")
bot.load_extension("ryan.exts.galoon")
bot.load_extension("ryan.exts.seasons")


@bot.command(name="help")
async def custom_help(ctx: commands.Context) -> None:
    """Custom help command with basic information."""
    help_embed = discord.Embed(colour=discord.Colour.green())

    # Field: bot name & icon
    help_embed.set_author(name="Ryan ~ real human bean", icon_url=bot.user.avatar_url)

    # Field: revision
    help_embed.add_field(name="Revision:", value=f"`{revision}`")

    # Field: active extensions
    active_cogs = "\n".join(cog for cog in bot.cogs)
    help_embed.add_field(name="Active extensions:", value=active_cogs, inline=False)

    # Field: footer
    help_embed.set_footer(text=f"Awakened {bot.start_time.humanize(arrow.utcnow())}")

    await ctx.send(embed=help_embed)


bot.run(Secrets.bot_token)
