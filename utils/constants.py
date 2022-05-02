FETCHED_MEMBERS_FILE = "fetched_data.json"

CONFIG_NAMES = ["config.json", FETCHED_MEMBERS_FILE]

DISCORD_API_URL = "https://discord.com/api/v9"

ROUTES = ["discord.oauth", "discord.users"]


class OAuth:
    SCOPE = "identify guilds"
