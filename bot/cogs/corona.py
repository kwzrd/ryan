import logging
import typing as t
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands, tasks

from bot.bot import Bot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def cute_dict(dct: t.Dict[str, str]) -> str:
    """Make `dct` readable in Discord's markdown."""
    return "\n".join(f"**{key.capitalize()}**: {value}" for key, value in dct.items())


class Corona(commands.Cog):
    """Wrapper for coronavirus API.

    See: https://github.com/javieraviles/covidapi
    """

    INTERVAL = 15

    url_all = "https://coronavirus-19-api.herokuapp.com/all"
    url_countries = "https://coronavirus-19-api.herokuapp.com/countries"

    all: t.Dict[str, t.Any]
    countries: t.Dict[str, t.Dict[str, t.Any]]

    last_refresh: t.Optional[datetime]

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.refresh.start()

    async def get(self, url: str) -> t.Any:
        """Make a GET request to `url` and return response parsed json."""
        logger.info(f"Get: {url}")
        try:
            async with self.bot.http_session.get(url) as resp:
                return await resp.json()
        except aiohttp.ClientError as exc:
            logger.error(f"Get failed: {exc}")
            return None

    @tasks.loop(minutes=INTERVAL)
    async def refresh(self) -> None:
        """Periodically refresh & cache counts."""
        logger.info(f"Refreshing cache")
        self.all = await self.get(self.url_all) or {}

        country_list = await self.get(self.url_countries) or []
        self.countries = {
            record["country"].casefold(): record
            for record in country_list
        }

        self.last_refresh = datetime.now()

    @commands.command(name="corona", aliases=["covid"])
    async def corona_cmd(self, ctx: commands.Context, *, country: t.Optional[str] = None) -> None:
        """Give cached information about the covid."""
        if country is None:
            title = "General stats"
            descr = await cute_dict(self.all) or "Cache empty"
            color = discord.Colour.green() if self.all else discord.Colour.red()

        elif record := self.countries.get(country.casefold()):
            title = f"Stats for {country.title()}"
            descr = await cute_dict(record) or "Cache empty"
            color = discord.Colour.green()

        else:
            title = "Country not found"
            descr = f"Available: {', '.join(self.countries) if self.countries else 'none (cache empty)'}"
            color = discord.Colour.red()

        response = discord.Embed(title=title, description=descr, color=color)
        response.set_footer(text=f"Last refresh: {self.last_refresh}")

        await ctx.send(embed=response)


def setup(bot: Bot) -> None:
    """Load Corona cog."""
    bot.add_cog(Corona(bot))
