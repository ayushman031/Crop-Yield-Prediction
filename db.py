"""Configurable PyMongo connection."""
import os
from pymongo import MongoClient
client = MongoClient(os.getenv("MONGODB_URI","mongodb://localhost:27017/"),
                     serverSelectionTimeoutMS=5000)
db = client["crop_yield_db"]
crop_collection = db["crop_records"]
