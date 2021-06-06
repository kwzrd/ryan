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


class ConfigError(RuntimeError):
    pass


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

        Raise errors when `section_name` is not present in `data`, or an annotated
        attribute is not present in the chosen section. CI checks should ensure that
        broken config never reaches production.
        """
        log.info(f"Loading config: {type(self).__name__!r} (section: {section_name!r})")

        if section_name not in data:
            raise ConfigError(f"Section '{section_name}' is not present in config!")

        section = data[section_name]

        for attr_name in self.__annotations__:

            if attr_name not in section:
                raise ConfigError(
                    f"Attribute '{attr_name}' not found in section '{section_name}'!"
                )

            setattr(self, attr_name, section[attr_name])


class _Channels(_ConfigBase):
    """Discord channel IDs."""

    gallonmate_rolls: int
    gallonmate_announce: int


Channels = _Channels(section_name="channels")


class _Emoji(_ConfigBase):
    """Discord emoji codes & IDs."""

    galooned: str
    tips_fedora: str
    ok_hand: str
    weary: str
    angry: str
    frown: str
    upside_down: str
    pensive: str


Emoji = _Emoji(section_name="emoji")


class _Guilds(_ConfigBase):
    """Discord guilds IDs."""

    tree_society: int


Guilds = _Guilds(section_name="guilds")


class _Images(_ConfigBase):
    """Images links."""

    coronavirus: str
    gm_creepy: str


Images = _Images(section_name="images")


class _Users(_ConfigBase):
    """Discord user IDs."""

    gallonmate: int
    kwzrd: int


Users = _Users(section_name="users")
