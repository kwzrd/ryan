import random
from datetime import datetime

import discord

from ryan.constants import Images

TITLE_SUCCESS = (
    "Good point",
    "Great moves Ethan",
    "Keep it up",
    "Life is excellent!",
    "The daemon congratulates you",
)
TITLE_ERROR = (
    "Galooned again",
    "Put on full blast",
    "Reduced you to memes",
    "Get in the kiln",
    "Idk & dunno",
    "Something wrong",
    "I hold my head",
)


def msg_success(message: str) -> discord.Embed:
    """Create a success embed with `message`."""
    embed = discord.Embed(
        description=message,
        colour=discord.Colour.green(),
    )
    embed.set_author(name=random.choice(TITLE_SUCCESS), icon_url=Images.gm_creepy)
    return embed


def msg_error(message: str) -> discord.Embed:
    """Create an error embed with `message`."""
    embed = discord.Embed(
        description=message,
        colour=discord.Colour.red(),
    )
    embed.set_author(name=random.choice(TITLE_ERROR), icon_url=Images.gm_creepy)
    return embed


async def relay_message(message: discord.Message, target: discord.TextChannel) -> None:
    """Relays a quote embed to the `target` channel."""
    author = message.author
    if author.display_name != author.name:
        name = f"{author.display_name} ({author.name})"
    else:
        name = author.name

    quote_embed = discord.Embed(description=message.content)
    quote_embed.set_author(
        name=name,
        icon_url=author.avatar_url
    )
    quote_embed.set_footer(
        text=f"{datetime.now()} - {message.guild.name} - {message.channel.name}"
    )
    if message.attachments:
        quote_embed.add_field(
            name="Attachments:",
            value="\n".join(message.attachments)
        )

    await target.send(embed=quote_embed)
