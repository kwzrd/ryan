import logging
import sys

log_format = "{levelname}:{asctime}:{name}:{msg}"
dt_format = "%d/%m/%y:%H.%M.%S"
logging.basicConfig(stream=sys.stdout, level=logging.WARNING, format=log_format, style="{", datefmt=dt_format)
