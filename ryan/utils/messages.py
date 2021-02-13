import logging
import random
import typing as t
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

log = logging.getLogger(__name__)


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


async def download_file(attachment: discord.Attachment) -> t.Optional[discord.File]:
    """
    Download & return `attachment` file.

    If the download fails, the reason is logged and None will be returned.
    """
    log.debug(f"Attempting to download attachment: {attachment.url}")
    try:
        return await attachment.to_file()
    except discord.HTTPException as http_exc:
        log.warning("Failed to download attachment!", exc_info=http_exc)


async def relay_message(message: discord.Message, target: discord.TextChannel) -> None:
    """
    Relays an embed quoting `message` to the `target` channel.

    If the `message` contains attachments, the first one will be sent with the quotation.
    User-sent messages do not normally contain multiple attachments, so this case is ignored.
    """
    author = message.author  # For short since we'll access this a lot
    log.debug(f"Building quotation embed for message from: {author}")

    if author.display_name != author.name:
        name = f"{author.display_name} ({author.name})"
    else:
        name = author.name

    quote_embed = discord.Embed(description=message.content)
    quote_embed.set_author(name=name, icon_url=author.avatar_url)
    quote_embed.set_footer(text=f"{datetime.now()} - {message.guild.name} - {message.channel.name}")

    if message.attachments:
        log.debug(f"Relaying first of {len(message.attachments)} attachments")
        attachment = message.attachments[0]  # We will only relay the first attachment

        if (att_file := await download_file(attachment)) is not None:
            quote_embed.set_image(url=f"attachment://{attachment.filename}")  # Embed displays the attached file
    else:
        log.debug("Message contains no attachments")
        att_file = None

    log.debug("Dispatching quotation embed")
    await target.send(embed=quote_embed, file=att_file)
