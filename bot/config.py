import json

with open("config.json", "r") as config_file:
    cfg = json.load(config_file)


class Config:
    token: str = cfg["token"]
