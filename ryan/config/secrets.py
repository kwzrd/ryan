import logging
from os import environ

log = logging.getLogger(__name__)


class _Secrets:
    """Runtime abstraction exposing environment variables."""

    bot_token: str  # Discord login token
    bot_prefix: str  # Command prefix

    def __init__(self) -> None:
        """Load secrets from environment & set as attributes."""
        log.info("Loading secrets from environment")

        required_keys = ("BOT_TOKEN",)
        if any(key not in environ.keys() for key in required_keys):
            raise Exception(f"Environment lacks required variables: {required_keys}")

        self.bot_token = str(environ.get("BOT_TOKEN"))
        self.bot_prefix = str(environ.get("BOT_PREFIX", "?"))


Secrets = _Secrets()
