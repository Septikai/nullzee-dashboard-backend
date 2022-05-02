import pymongo
import time

import runtime_config
from config_manager import save_fetched_data
from utils.discord_api import fetch_multiple_guild_members_or_users


def add_user_objects(db_users):
    user_ids = [z["_id"] for z in db_users]
    members = fetch_multiple_guild_members_or_users(user_ids, 100)

    ids = set(members.keys())
    for member in members:
        if "is_member" in members[member] and members[member]["is_member"]:
            if "user" not in members[member]:
                print(f"PROBLEM - {members[member]}")
    db_users = [z | {"user": members[z["_id"]]["user"] if members[z["_id"]]["is_member"] else members[z["_id"]]}
                for z in db_users if z["_id"] in ids]
    db_users = [z | {"nick": members[z["_id"]]["nick"] if members[z["_id"]]["is_member"] else None}
                for z in db_users if z["_id"] in ids]
    db_users = [z | {"colour": members[z["_id"]]["colour"] if members[z["_id"]]["is_member"] else None}
                for z in db_users if z["_id"] in ids]

    return db_users


def get_user_collection(sort=None, direction=pymongo.DESCENDING, save=True):
    if runtime_config.fetched_leaderboard_data[sort] != {} and \
       time.time() - runtime_config.fetched_leaderboard_data[sort]["fetched_at"] < 172800:
        return runtime_config.fetched_leaderboard_data[sort]

    data = runtime_config.mongodb_user_collection.find({})

    if sort == "levels":
        data.sort([("level", direction), ("experience", direction)])
    elif sort == "points":
        data.sort(("points", direction))
    elif sort == "vc_minutes":
        data.sort(("vc_minutes", direction))

    data = [z for z in data]

    if save:
        data_dict = {"data": data, "fetched_at": time.time()}
        runtime_config.fetched_leaderboard_data[sort] = data_dict
        save_fetched_data()

    return data


def get_user_collection_with_user_objects(sort=None, direction=pymongo.DESCENDING):
    if runtime_config.fetched_leaderboard_data[sort] != {} and \
       time.time() - runtime_config.fetched_leaderboard_data[sort]["fetched_at"] < 172800:
        return runtime_config.fetched_leaderboard_data[sort]

    raw_data = get_user_collection(sort, direction, False)

    data = add_user_objects(raw_data)

    data_dict = {"data": data, "fetched_at": time.time()}
    runtime_config.fetched_leaderboard_data[sort] = data_dict
    save_fetched_data()

    return data
