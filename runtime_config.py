from flask import Flask
from pymongo import MongoClient

# Configuration

# MongoDB connection URI.
# From: config_manager.py
mongodb_connection_string: str = ""
mongodb_database_name: str = ""
mongodb_user_collection_name: str = ""
mongodb_moderation_collection_name: str = ""
mongodb_giveaway_collection_name: str = ""


# From: mongodb.py
mongodb_client: MongoClient = None
mongodb_database = None
mongodb_user_collection = None
mongodb_moderation_collection = None
mongodb_giveaway_collection = None

# Flask app.
# From: app.py
app: Flask = None

# Discord config values
# From config_manager.py
discord_oauth: dict = None
discord_guild_id: int = None

# Allowed domains for cors-protected endpoints
# From config_manager.py
cors_host: str = "*"

# Discord Bot Secret
# From config_manager.py
bot_token: str = ""

# Fetched Members and Users
# From fetched_data.json
fetched_members: dict = None
fetched_users: dict = None
fetched_leaderboard_data: dict = None
fetched_guild_roles: dict = None
