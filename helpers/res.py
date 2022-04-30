import flask
import json as jsonlib  # Name conflict with the function name


def json(body=None, headers=None, code=200, **kwargs):
    if headers is None:
        headers = {}
    if body is None:
        body = {"success": False}
    headers.update({"Content-Type": "application/json"})
    response = flask.Response(response=jsonlib.dumps(body), status=code, headers=headers, mimetype="application/json")
    return response
