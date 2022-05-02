import pymongo
from flask import Flask

from helpers import res, cors
import runtime_config
from utils.mongo import get_user_collection, get_user_collection_with_user_objects
from utils.discord_api import fetch_guild_member_or_user, fetch_multiple_guild_members_or_users, get_guild_roles,\
    get_member_colour_role


def setup(app: Flask):

    @app.route("/users/<user_id>")
    @cors.site()
    def discord_user(user_id: str):
        if not user_id.isdigit():
            return res.json(code=404)
        print(runtime_config.fetched_members)
        member = fetch_guild_member_or_user(user_id)
        if "member" in member:
            member = member["member"]
        else:
            member = member["user"]

        # TODO: implement a check for if the user does not have a db entry
        user_coll_entry = runtime_config.mongodb_user_collection.find_one({"_id": user_id})

        print(member)
        print(user_coll_entry)

        return res.json({
            "member_info": member,
            "db_info": user_coll_entry,
        })

    @app.route("/users/<user_id>/punishments")
    @cors.site()
    def user_punishments(user_id: str):
        if not user_id.isdigit():
            return res.json(code=404)

        # TODO: implement a check for if the user does not have a db entry
        user_coll_entry = list(runtime_config.mongodb_moderation_collection.find({"offender_id": int(user_id)}, sort=[("_id", pymongo.DESCENDING)]))
        user_coll_entry = [{key: value for key, value in d.items() if key != "_id"} for d in user_coll_entry]
        for d in user_coll_entry:
            d.update((k, str(v)) for k, v in d.items() if k == "mod_id")

        to_fetch = [p["mod_id"] for p in user_coll_entry]
        mods = fetch_multiple_guild_members_or_users(to_fetch)

        for punishment in user_coll_entry:
            if "user" in mods[punishment["mod_id"]]:
                punishment["mod_pfp"] = mods[punishment["mod_id"]]["user"]["avatar"]
                punishment["mod_username"] = f"{mods[punishment['mod_id']]['user']['username']}#" \
                                             f"{mods[punishment['mod_id']]['user']['discriminator']}"
            else:
                punishment["mod_pfp"] = mods[punishment["mod_id"]]["avatar"]
                punishment["mod_username"] = f"{mods[punishment['mod_id']]['username']}#" \
                                             f"{mods[punishment['mod_id']]['discriminator']}"

        print(f"punishments - {user_coll_entry}")

        return res.json({
            "punishments": user_coll_entry
        })

    @app.route("/users/leaderboard/levels")
    @cors.site()
    def users_leaderboard_by_levels():
        users_by_level = get_user_collection_with_user_objects(sort="levels")

        return res.json({
            "users_by_level": users_by_level
        })

    @app.route("/users/leaderboard/points")
    @cors.site()
    def users_leaderboard_by_points():
        users_by_points = get_user_collection_with_user_objects(sort="points")

        return res.json({
            "users_by_points": users_by_points
        })

    @app.route("/users/leaderboard/vc_time")
    @cors.site()
    def users_leaderboard_by_vc_time():
        user_by_vc_time = get_user_collection_with_user_objects(sort="vc_minutes")

        return res.json({
            "user_by_vc_time": user_by_vc_time
        })
