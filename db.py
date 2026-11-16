from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["crop_yield_db"]
crop_collection = db["crop_records"]

try:
    client.admin.command("ping")
    print("MongoDB connected")
except Exception as e:
    print("MongoDB not connected", e)
