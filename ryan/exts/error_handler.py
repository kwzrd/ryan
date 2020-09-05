import contextlib
import logging
import random
import typing as t

from discord import DiscordException
from discord.ext import commands

from ryan.bot import Ryan
from ryan.constants import Emoji
from ryan.utils import msg_error

log = logging.getLogger(__name__)

ErrorMessage = t.Tuple[t.Type[Exception], str]

MESSAGES: t.Tuple[ErrorMessage, ...] = (
    (commands.CommandNotFound,    "No such command exists"),                               # noqa: E241
    (commands.UserInputError,     "Command was invoked with invalid parameters {emoji}"),  # noqa: E241
    (commands.CheckFailure,       "Permission check failed {emoji}"),                      # noqa: E241
    (commands.DisabledCommand,    "Command is currently disabled!"),                       # noqa: E241
    (commands.CommandInvokeError, "Command failed to execute {emoji}"),                    # noqa: E241
    (commands.CommandOnCooldown,  "Command is currently on cooldown!"),                    # noqa: E241
)
FALLBACK = "Unexpected exception handled, see log for details"

EMOJI_POOL = (Emoji.weary, Emoji.angry, Emoji.frown, Emoji.upside_down, Emoji.pensive)


def random_emoji() -> str:
    """Draw random emoji from `EMOJI_POOL`."""
    return random.choice(EMOJI_POOL)


def match_response(exception_instance: Exception) -> str:
    """
    Match `exception_instance` to a response message, if defined in `MESSAGES`.

    If not match is found, `FALLBACK` is returned instead - some response is always given.

    The reason why `MESSAGES` isn't a mapping is that using the types as keys would disallow
    the use of `isinstance` to correctly recognize subclasses.
    """
    log.debug(f"Matching exception: {type(exception_instance)}")

    for exception_type, response in MESSAGES:

        if isinstance(exception_instance, exception_type):
            log.debug(f"Exception matched to type: {exception_type} (message: {response})")

            # If the string contains an emoji placeholder, inject a random one,
            # but otherwise we do nothing (exc raised on no placeholder)
            with contextlib.suppress(KeyError):
                response = response.format(emoji=random_emoji())
                log.debug(f"Injected emoji: {response}")

            return response

    log.debug(f"No match found, using fallback: {FALLBACK}")
    return FALLBACK


class ErrorHandler(commands.Cog):
    """Generic error handler."""

    def __init__(self, bot: Ryan) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Send message to `ctx` and log `error`.

        Response is matched based on `error` type. If an `original` attr is carried, it will be logged,
        but its message will not propagate to the user.

        In case we do not match `error` to anything, a generic response `FALLBACK` is used as response.
        """
        original_exception = getattr(error, "original", None)
        log.debug(f"Error handler received exception of type: {type(error)}, original: {type(original_exception)}")

        # This guarantees to always return some string - a fallback is used when no match is found
        response = match_response(error)

        # Use the generic error response generator, which wraps the message in a red embed
        response_embed = msg_error(response)

        # The bot may not be able to respond, e.g. due to permissions - let's be safe
        try:
            await ctx.send(embed=response_embed)
        except DiscordException as response_error:
            log.exception("Failed to send response embed", exc_info=response_error)

        # The idea is to only log the full traceback if we've encountered a non-Discord exception
        # This may need to be revisited at some point in the future - maybe we need more information
        if original_exception is not None:
            log.exception("Error handler received non-Discord exception", exc_info=error)


def setup(bot: Ryan) -> None:
    """Load ErrorHandler cog."""
    bot.add_cog(ErrorHandler(bot))
