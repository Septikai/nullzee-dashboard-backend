import flask_cors

import runtime_config


def site():
    print("CORS here")
    return flask_cors.cross_origin(
        origins=runtime_config.cors_host,
        supports_credentials=True,
    )
