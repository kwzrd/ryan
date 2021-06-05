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


class _ConfigBase:
    """
    Base class for runtime config abstraction.

    The base class is responsible for providing the initialisation logic. Subclasses
    can then be entirely declarative, only specifying which attributes should be drawn
    from the source file using annotations.
    """

    def __init__(self, section_name: str) -> None:
        """
        Load annotations into attributes from `section_name` in `data`.

        Lookups are naive and will raise errors. CI checks should ensure that broken
        config never reaches production.
        """
        log.info(f"Loading config: {type(self).__name__!r} (section: {section_name!r})")
        section = data[section_name]

        for attr_name in self.__annotations__:
            setattr(self, attr_name, section[attr_name])
