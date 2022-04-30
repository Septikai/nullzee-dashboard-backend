from flask import Flask, request
import requests

from helpers import res, cors
import runtime_config
from utils.constants import DISCORD_API_URL, OAuth
from utils.json_wrapper import JsonWrapper


def exchange_code(code, redirect_uri):
    data = {
        "client_id": str(runtime_config.discord_oauth["client_id"]),
        "client_secret": runtime_config.discord_oauth["client_secret"],
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": OAuth.SCOPE
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post(f"{DISCORD_API_URL}/oauth2/token", data=data, headers=headers)
    return r.json()


def auth_request(endpoint, access_token, auth_type) -> JsonWrapper or list:
    headers = {
        "Authorization": f"{auth_type} {access_token}"
    }
    r = requests.get(f"{DISCORD_API_URL}/{endpoint}", headers=headers).json()
    if isinstance(r, dict):
        return JsonWrapper.from_dict(r)
    else:
        return r


def get_user(access_token):
    return auth_request("users/@me", access_token, "Bearer")


def get_user_guilds(access_token):
    return auth_request("users/@me/guilds", access_token, "Bearer")


def get_guild_member(member_id):
    return auth_request(f"guilds/{runtime_config.discord_guild_id}/members/{member_id}",
                        runtime_config.bot_token, "Bot")


def get_guild_roles():
    return auth_request(f"guilds/{runtime_config.discord_guild_id}/roles",
                        runtime_config.bot_token, "Bot")


def get_member_colour(common_roles):
    common_roles.reverse()
    filtered = list(filter(lambda d: d["color"] is not None and d["color"] != 0,
                           sorted(common_roles, key=lambda d: d["position"], reverse=True)))
    return filtered[0]


def setup(app: Flask):
    @app.route("/oauth_callback")
    @cors.site()
    def discord_oauth_endpoint():
        query = request.args
        code = query.get("code", None)
        if code is None:
            return res.json(code=401)
        redirect_uri = query.get("redirect_uri", runtime_config.discord_oauth["redirect_uri"])
        discord_access_token = exchange_code(code, redirect_uri).get("access_token", None)
        if discord_access_token is None:
            return res.json(code=403)
        user, guilds = get_user(discord_access_token), get_user_guilds(discord_access_token)
        member = get_guild_member(user["id"])

        # TODO: implement a check for if the user does not have a db entry
        user_coll_entry = runtime_config.mongodb_user_collection.find_one({"_id": str(user["id"])})

        # Roles

        guild_roles = get_guild_roles()
        guild_role_ids = [r["id"] for r in guild_roles]
        common_role_ids = list(set(guild_role_ids).intersection(member["roles"]))
        common_roles = [role for role in guild_roles if role["id"] in common_role_ids]
        common_roles_dict = {role["id"]: role for role in common_roles}
        member["roles"] = common_roles_dict

        # Colour

        top_colour = get_member_colour(common_roles)["color"]
        user["colour"] = f"{top_colour:x}"
        member["colour"] = f"{top_colour:x}"

        guild = list(filter(lambda g: g["id"] == str(runtime_config.discord_guild_id), guilds))[0]
        member["is_staff"] = int(guild["permissions"]) & 0x2000 == 0x2000

        print(user)
        print(member)
        print(user_coll_entry)
        print(guilds)

        return res.json({
            "user_info": user.to_dict(),
            "member_info": member,
            "db_info": user_coll_entry,
            "user_guilds": guilds
        })



