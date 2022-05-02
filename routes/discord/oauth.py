from flask import Flask, request
import requests

from helpers import res, cors
import runtime_config
from utils.constants import DISCORD_API_URL, OAuth
from utils.json_wrapper import JsonWrapper
from utils.discord_api import bot_auth_request, fetch_guild_member_or_user, get_member_colour_role, get_guild_roles,\
    exchange_code, get_current_user, get_current_user_guilds


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
        user, guilds = get_current_user(discord_access_token), get_current_user_guilds(discord_access_token)
        member = fetch_guild_member_or_user(user["id"], force=True)["member"]

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

        top_colour = get_member_colour_role(common_roles)["color"]
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



