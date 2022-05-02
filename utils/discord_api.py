import requests
import time

import runtime_config
from utils.json_wrapper import JsonWrapper
from utils.constants import DISCORD_API_URL, OAuth
from config_manager import save_fetched_data


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


def bearer_auth_request(endpoint, access_token) -> JsonWrapper or list:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    r = requests.get(f"{DISCORD_API_URL}/{endpoint}", headers=headers).json()
    if isinstance(r, dict):
        return JsonWrapper.from_dict(r)
    else:
        return r


def get_current_user(access_token):
    return bearer_auth_request("users/@me", access_token)


def get_current_user_guilds(access_token):
    return bearer_auth_request("users/@me/guilds", access_token)


def bot_auth_request(endpoint, access_token) -> JsonWrapper or list:
    headers = {
        "Authorization": f"Bot {access_token}"
    }
    r = requests.get(f"{DISCORD_API_URL}/{endpoint}", headers=headers).json()
    if isinstance(r, dict):
        return JsonWrapper.from_dict(r)
    else:
        return r


def get_guild_roles():
    if runtime_config.fetched_guild_roles != {} and \
       time.time() - runtime_config.fetched_guild_roles["fetched_at"] < 172800:
        return runtime_config.fetched_guild_roles["data"]

    guild_roles = bot_auth_request(f"guilds/{runtime_config.discord_guild_id}/roles", runtime_config.bot_token)

    runtime_config.fetched_guild_roles = {"data": guild_roles, "fetched_at": time.time()}

    return guild_roles


def get_member_colour_role(common_roles):
    common_roles.reverse()
    filtered = list(filter(lambda d: d["color"] is not None and d["color"] != 0,
                           sorted(common_roles, key=lambda d: d["position"], reverse=True)))
    return filtered[0]


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
            del fetched["member"]
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
    if "member" in fetched and len(fetched["member"]["roles"]) > 0:
        guild_roles = get_guild_roles()
        guild_role_ids = [r["id"] for r in guild_roles]
        common_role_ids = list(set(guild_role_ids).intersection(fetched["member"]["roles"]))
        common_roles = [role for role in guild_roles if role["id"] in common_role_ids]
        common_roles_dict = {role["id"]: role for role in common_roles}
        fetched["member"]["roles"] = common_roles_dict
        top_colour = get_member_colour_role(common_roles)["color"]
        fetched["member"]["colour"] = f"{top_colour:x}"
    else:
        fetched["user"]["roles"] = None
        fetched["user"]["colour"] = "#FFFFFF"
    if save:
        save_fetched_data()
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
        if limit is not None and count >= limit:
            break
        else:
            if "member" in fetched:
                time.sleep(0.02)
            else:
                time.sleep(0.04)
    save_fetched_data()
    print(f"fetched {len(members)}{f'/{limit}' if limit is not None else ''} - {members}")
    return members
