import logging
import os
from datetime import datetime
from pathlib import Path

# Logs are are saved to project_root/logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Each run will have a distinct log file named using current UTC datetime in ISO format
FILE = Path(LOG_DIR, f"{datetime.utcnow().isoformat()}.log")

# Define custom log format
FORMAT = logging.Formatter(
    fmt="{levelname} | {asctime} | {name} | {msg}",
    datefmt="%d/%m/%y %H:%M:%S",
    style="{",  # Style arg enables f-string syntax
)
ENCODING = "UTF-8"

# We'll log both to stdout and to our run file
handle_console = logging.StreamHandler()  # Defaults to stdout
handle_file = logging.FileHandler(FILE, encoding=ENCODING)

# By default we listen to info and above, unless the 'DEBUG' env var is set to something truthy
root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG if os.environ.get("DEBUG") else logging.INFO)

# Now we register both handlers with the root logger
for handler in (handle_console, handle_file):
    root_log.addHandler(handler)

    # Handlers can listen at all levels as we'll be filtering messages
    # at logger instance level (before they reach the handler)
    handler.setLevel(logging.DEBUG)

    # Apply our custom formatter
    handler.setFormatter(FORMAT)

# We'll manually raise 3rd party log levels, as we're not interested in their info level
to_raise = ("aiosqlite", "asyncio", "discord", "websockets")
for log_name in to_raise:
    logging.getLogger(log_name).setLevel(logging.WARNING)
