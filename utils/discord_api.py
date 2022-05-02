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


def fetch_guild_member_or_user(member_id, save=True, force=False):
    initial_fetched = None
    if not force:
        if member_id in runtime_config.fetched_members and \
           time.time() - runtime_config.fetched_members[member_id]["fetched_at"] < 172800:
            initial_fetched = {"member": runtime_config.fetched_members[member_id]}
            print(f"retrieved - {initial_fetched}")
        if (initial_fetched is None or "code" in initial_fetched["member"]) and \
           member_id in runtime_config.fetched_users and \
           time.time() - runtime_config.fetched_users[member_id]["fetched_at"] < 172800:
            initial_fetched = {"user": runtime_config.fetched_users[member_id]}
            print(f"retrieved - {initial_fetched}")
    if initial_fetched is None:
        fetched = {"member": get_guild_member_from_api(member_id)}
        fetched["member"]["fetched_at"] = time.time()
        fetched["member"]["is_member"] = True
        if "code" in fetched["member"] and fetched["member"]["code"] == 10007:
            fetched["user"] = get_user_from_api(member_id)
            fetched["user"]["fetched_at"] = time.time()
            fetched["user"]["is_member"] = False
            if "code" in fetched["user"]:
                print(f"FAIL - {fetched['member']}")
                print(f"CONT. - {fetched['user']}")
                return -1
        if "member" in fetched and "user" not in fetched:
            runtime_config.fetched_members[member_id] = fetched["member"]
        if "user" in fetched:
            runtime_config.fetched_users[member_id] = fetched["user"]
        print(f"fetched - {fetched}")
    else:
        fetched = initial_fetched
    if "member" in fetched and "retry_after" in fetched["member"]:
        print(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA - {fetched}")
        time.sleep(fetched["member"]["retry_after"] + 0.1)
        fetched = fetch_guild_member_or_user(member_id, save, force)
    if "user" in fetched and "retry_after" in fetched["user"]:
        print(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA - {fetched}")
        time.sleep(fetched["user"]["retry_after"] + 0.1)
        fetched = fetch_guild_member_or_user(member_id, save, force)
    if save:
        save_fetched_members()
    return fetched


def fetch_multiple_guild_members_or_users(member_ids, limit=None):
    members = {}
    count = 0
    for member_id in member_ids:
        fetched = fetch_guild_member_or_user(member_id, save=False)
        if fetched != -1:
            if "member" in fetched:
                members[member_id] = fetched["member"]
            else:
                members[member_id] = fetched["user"]
        count += 1
        if count is not None and count >= limit:
            break
        else:
            if "member" in fetched:
                time.sleep(0.02)
            else:
                time.sleep(0.04)
    save_fetched_members()
    print(f"fetched {len(members)}{f'/{limit}' if limit is not None else ''} - {members}")
    return members
