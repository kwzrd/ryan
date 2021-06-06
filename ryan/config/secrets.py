import logging
from os import environ

log = logging.getLogger(__name__)


class _Secrets:
    """Runtime abstraction exposing environment variables."""

    bot_token: str  # Discord login token

    def __init__(self) -> None:
        """Load secrets from environment & set as attributes."""
        log.info("Loading secrets from environment")

        for attr_name in self.__annotations__:
            lookup_name = attr_name.upper()  # Conventionally environment variables are uppercase.

            if lookup_name not in environ:
                raise RuntimeError(f"Environment variable missing: '{lookup_name}'")

            setattr(self, attr_name, environ[lookup_name])


Secrets = _Secrets()
