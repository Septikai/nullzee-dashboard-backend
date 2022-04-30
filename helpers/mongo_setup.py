from pymongo import MongoClient
import runtime_config


def setup():
    runtime_config.mongodb_client = MongoClient(runtime_config.mongodb_connection_string)
    runtime_config.mongodb_database = runtime_config.mongodb_client[runtime_config.mongodb_database_name]
    runtime_config.mongodb_user_collection = runtime_config.mongodb_database[runtime_config.mongodb_user_collection_name]
    runtime_config.mongodb_moderation_collection = runtime_config.mongodb_database[runtime_config.mongodb_moderation_collection_name]
    runtime_config.mongodb_giveaway_collection = runtime_config.mongodb_database[runtime_config.mongodb_giveaway_collection_name]