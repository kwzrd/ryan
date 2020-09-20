import os


class Emoji:
    """
    Emoji code constants recognizable by Discord.

    For the custom ones, the bot must be in a guild where the emoji are defined.
    """

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


class Users:
    gallonmate = 209018651360100352
    kwzrd = 144912469071101952


class Guilds:
    tree_society = 319955430732464128


class Channels:
    gallonmate_rolls = 484118447073132574
    gallonmate_announce = 319955430732464128


class Client:
    token: str = os.environ["TOKEN"]
    prefix: str = os.environ["PREFIX"]


class Images:
    gm_creepy = (
        "https://cdn.discordapp.com/attachments/319955430732464128/695021552520921148/"
        "Screenshot_20200327-184350_FaceApp.jpg"
    )
