from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure
from config import MONGO_URI, DATABASE_NAME

# Simple database setup
client = None
db = None
users_collection = None
traffic_collection = None


def connect_db():
    global client, db, users_collection, traffic_collection
    try:
        client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
        client.admin.command("ping")
        db = client[DATABASE_NAME]
        users_collection = db["users"]
        traffic_collection = db["traffic_data"]
        print("✅ MongoDB connected successfully")
        return True
    except ConnectionFailure:
        print("❌ MongoDB connection failed")
        return False


def serialize_doc(doc):
    """Convert ObjectId to string"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc
