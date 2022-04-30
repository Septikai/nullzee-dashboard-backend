import runtime_config

import json


def read_config(path: str) -> None:
    with open(path) as f:
        config = json.load(f)
        for key in config:
            setattr(runtime_config, key, config[key])
