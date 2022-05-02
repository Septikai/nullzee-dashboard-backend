import json

import runtime_config
from utils.constants import FETCHED_MEMBERS_FILE


def read_config(paths: str) -> None:
    for path in paths:
        with open(path) as f:
            config = json.load(f)
            for key in config:
                setattr(runtime_config, key, config[key])


def save_fetched_data():
    with open(FETCHED_MEMBERS_FILE, "w") as f:
        fetched_json = {
            "fetched_members": runtime_config.fetched_members,
            "fetched_users": runtime_config.fetched_users,
            "fetched_leaderboard_data": runtime_config.fetched_leaderboard_data
        }
        json.dump(fetched_json, f)
