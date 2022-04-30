from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import importlib
from waitress import serve

from utils.constants import CONFIG_NAME, ROUTES
import runtime_config
import config_reader
from helpers import mongo_setup

config_reader.read_config(CONFIG_NAME)

# TODO: add auth before release so you can't just make any call you can imagine to the api and have it return everything


def setup():
    api_app = Flask(__name__)
    app = DispatcherMiddleware(Flask("dummy_app"), {
        "/api": api_app
    })

    mongo_setup.setup()

    for route in ROUTES:
        module = importlib.import_module(f"routes.{route}")
        # noinspection PyUnresolvedReferences
        module.setup(api_app)

    runtime_config.app = app

    def start():
        serve(app, threads=4, port=80)

    start()


def main():
    setup()


if __name__ == "__main__":
    main()
