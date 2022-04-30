from flask import Flask
from pymongo import MongoClient

# Configuration

# MongoDB connection URI.
# From: config_reader.py
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
# From config_reader.py
discord_oauth: dict = None
discord_guild_id: int = None

# Allowed domains for cors-protected endpoints
# From config_reader.py
cors_host: str = "*"

# Discord Bot Secret
# From config_reader.py
bot_token: str = ""
