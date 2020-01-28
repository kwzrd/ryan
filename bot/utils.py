import logging
from datetime import datetime

import discord


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
