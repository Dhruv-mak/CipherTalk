from pymongo import MongoClient
import os

client: MongoClient | None = None


def get_client() -> MongoClient:
    global client
    if client is None:
        MONGODB_URI = os.environ.get("DATABASE_URI")
        client = MongoClient(MONGODB_URI)
    return client


def close_client():
    global client
    if client is not None:
        client.close()
        client = None
