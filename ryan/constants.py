import os


class Channels:
    """Discord channel IDs."""

    gallonmate_rolls = 484118447073132574
    gallonmate_announce = 319955430732464128


class Client:
    """Relating to Discord connection."""

    token: str = os.environ["TOKEN"]
    prefix: str = os.environ["PREFIX"]


class Emoji:
    """Discord emoji codes & IDs."""

    # Custom emoji
    galooned = "<:galooned:338627421630627842>"
    tips_fedora = "<:pepetipsfedora:550466723997024267>"

    # Positive emotions
    ok_hand = ":ok_hand:"

    # Negative emotions
    weary = ":weary:"
    angry = ":angry:"
    frown = ":frowning:"
    upside_down = ":upside_down:"
    pensive = ":pensive:"


class Guilds:
    """Discord guilds IDs."""

    tree_society = 319955430732464128


class Images:
    """Images links."""

    coronavirus = "https://cdn.discordapp.com/attachments/746790524567945277/746790671557591070/coronavirus-5107715_1280.webp"  # noqa: E501
    gm_creepy = "https://cdn.discordapp.com/attachments/319955430732464128/695021552520921148/Screenshot_20200327-184350_FaceApp.jpg"  # noqa: E501


class Users:
    """Discord user IDs."""

    gallonmate = 209018651360100352
    kwzrd = 144912469071101952
