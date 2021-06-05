import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

environments = Path("ryan", "config", "environments")
available_files = {file.name: file for file in environments.glob("*.json")}

for option in ("production.json", "development.json"):
    if option in available_files:
        chosen_file: Path = available_files[option]
        break
else:
    raise RuntimeError("No configuration file was found!")

log.info(f"Chosen configuration file: '{chosen_file}'")

with chosen_file.open(mode="r", encoding="UTF-8") as file:
    data = json.load(file)
