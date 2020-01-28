import random
import logging
import string

import discord
from discord.ext import commands


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


seasons = {
    "christmas": (
        u"\U0001F384",  # tree
        u"\U0001F385",  # santa
        u"\U0001F98C",  # deer
        u"\U0001F381",  # gift
        u"\U00002744",  # snowflake
        u"\U00002603",  # snowman
    ),
    "easter": (
        u"\U0001F407",  # bunny
        u"\U0001F430",  # bunny face
        u"\U0001F423",  # hatching chick
        u"\U0001F331",  # seedling
        u"\U0001F95A",  # egg
        u"\U0001F36B",  # chocolate
    )
}


def decorate_name(discord_name: str, season_name: str) -> str:
    """Decorate a given string with emoji for current season.

    The used emoji and drawn randomly from the season given by `season_name`.
    Strips all other emoji from `discord_name` before decorating.
    """
    name = "".join(char for char in discord_name if char in string.printable)
    prefix, postfix = random.sample(population=seasons[season_name], k=2)
    return prefix + name + postfix


class Seasons(commands.Cog):
    """Decorates the server for various seasons.

    The guild name, channel names and member names will be decorated with
    emoji that are pre-defined for each season.
    """

    seasons_embed = discord.Embed.from_dict(
        {
            "title": "Available seasons",
            "color": discord.Colour.orange().value,
            "fields": [
                {
                    "name": season,
                    "value": "".join(e for e in emoji),
                    "inline": False,
                }
                for season, emoji in seasons.items()
            ]
        }
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def season(self, ctx: commands.Context, season_name: str = None) -> None:
        """Attempt to decorate the server.

        Many of the decorations may fail due to missing permissions. The bot handles
        this and returns an embed containing a report of how many decorations have
        failed.

        If `season_name` is not provided, or is invalid, an embed containing the
        available seasons will be returned.
        """
        if season_name is None or season_name not in seasons:
            await ctx.send(embed=self.seasons_embed)
            return

        g_success = None
        ch_fail, m_fail = 0, 0

        guild_name = decorate_name(ctx.guild.name, season_name)
        try:
            await ctx.guild.edit(name=guild_name)
        except discord.Forbidden:
            g_success = False
        else:
            g_success = True

        for channel in ctx.guild.channels:
            channel_name = decorate_name(channel.name, season_name)
            try:
                await channel.edit(name=channel_name)
            except discord.Forbidden:
                ch_fail += 1

        for member in ctx.guild.members:
            member_name = decorate_name(member.display_name, season_name)
            try:
                await member.edit(nick=member_name)
            except discord.Forbidden:
                m_fail += 1

        ch_success = len(ctx.guild.channels) - ch_fail
        m_success = len(ctx.guild.members) - m_fail

        response = discord.Embed(title="Season change completed", colour=discord.Colour.green())
        response.add_field(name="Guild name", value="Success" if g_success else "Missing permission", inline=False)
        response.add_field(name="Channels", value=f"Success: {ch_success}\nMissing permission: {ch_fail}", inline=False)
        response.add_field(name="Members", value=f"Success: {m_success}\nMissing permission: {m_fail}", inline=False)
        await ctx.send(embed=response)


def setup(bot: commands.Bot) -> None:
    """Load Seasons cog."""
    bot.add_cog(Seasons(bot))
    log.info("Seasons cog loaded")
