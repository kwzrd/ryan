import logging

FORMAT = logging.Formatter(
    fmt="{asctime} | {levelname} | {name} | {message}",
    datefmt="%d/%m/%y %H:%M:%S",
    style="{",  # Style arg enables f-string syntax.
)

# Prepare a stdout log sink.
handle_console = logging.StreamHandler()
handle_console.setLevel(logging.DEBUG)
handle_console.setFormatter(FORMAT)

# Now register our sink with the root log.
root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG)
root_log.addHandler(handle_console)

# Raise 3rd party log levels. We're not interested in their DEBUG & INFO logging.
to_raise = ("aiosqlite", "asyncio", "db_client", "discord", "websockets")
for log_name in to_raise:
    logging.getLogger(log_name).setLevel(logging.WARNING)

# Since we do not want to miss out on logging from config init, the initial import is
# deferred after the stdout sink is ready.
from ryan.config import App  # noqa: E402

if not App.log_debug:
    root_log.setLevel(logging.INFO)
