import requests
import time

import runtime_config
from utils.json_wrapper import JsonWrapper
from utils.constants import DISCORD_API_URL
from config_manager import save_fetched_members


def bot_auth_request(endpoint, access_token) -> JsonWrapper or list:
    headers = {
        "Authorization": f"Bot {access_token}"
    }
    r = requests.get(f"{DISCORD_API_URL}/{endpoint}", headers=headers).json()
    if isinstance(r, dict):
        return JsonWrapper.from_dict(r)
    else:
        return r


def get_guild_member_from_api(member_id):
    return bot_auth_request(f"guilds/{runtime_config.discord_guild_id}/members/{member_id}", runtime_config.bot_token)


def get_user_from_api(member_id):
    return bot_auth_request(f"users/{member_id}", runtime_config.bot_token)


def fetch_guild_member(member_id, save=True, force=False):
    initial_fetched = None
    if not force:
        if member_id in runtime_config.fetched_members and \
           time.time() - runtime_config.fetched_members[member_id]["fetched_at"] < 172800:
            initial_fetched = {"member": runtime_config.fetched_members[member_id]}
            print(f"retrieved - {initial_fetched}")
        if member_id in runtime_config.fetched_users and \
           time.time() - runtime_config.fetched_users[member_id]["fetched_at"] < 172800:
            initial_fetched = {"user": runtime_config.fetched_users[member_id]}
            print(f"retrieved - {initial_fetched}")
    if initial_fetched is None or "user" in initial_fetched:
        fetched = {"member": get_guild_member_from_api(member_id)}
        fetched["member"]["fetched_at"] = time.time()
        if "code" in fetched["member"] and fetched["member"]["code"] == 10007:
            if initial_fetched is not None and "user" in initial_fetched:
                fetched = initial_fetched
            else:
                fetched["user"] = get_user_from_api(member_id)
                fetched["user"]["fetched_at"] = time.time()
            if "code" in fetched["user"]:
                print(f"FAIL - {fetched['member']}")
                print(f"CONT. - {fetched['user']}")
                return -1
        if "member" in fetched:
            runtime_config.fetched_members[member_id] = fetched["member"]
        if "user" in fetched:
            runtime_config.fetched_users[member_id] = fetched["user"]
        print(f"fetched - {fetched}")
    else:
        fetched = initial_fetched
    if "retry_after" in fetched:
        time.sleep(fetched["retry_after"])
        fetched = fetch_guild_member(member_id, save, force)
    if save:
        save_fetched_members()
    return fetched


def fetch_multiple_guild_members(member_ids):
    members = {}
    for member_id in member_ids:
        fetched = fetch_guild_member(member_id, save=False)
        if fetched != -1:
            if "member" in fetched:
                fetched["member"]["is_member"] = True
                members[member_id] = fetched["member"]
            else:
                fetched["user"]["is_member"] = False
                members[member_id] = fetched["user"]
    save_fetched_members()
    print(f"fetched multiple - {members}")
    return members
