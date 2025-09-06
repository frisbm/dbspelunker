import json
import os

from pydantic import BaseModel


class Config(BaseModel):
    model: str
    token_limit: int
    location: str
    project_id: str


def load_config() -> Config:
    config_file = "config.json"

    for i in range(5):
        possible_path = os.path.join(*[".."] * i, config_file)
        if os.path.exists(possible_path):
            config_file = possible_path
            break

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_file, "r") as f:
        json_config = json.load(f)
        config = Config.model_validate(json_config)
        return config
