"""Demonstrate CREATE, READ, UPDATE, DELETE and rejected invalid input."""
import os
from uuid import uuid4
from pymongo import MongoClient
from pymongo.errors import WriteError
from schema_validation import ensure_schema

def main():
    client = MongoClient(os.getenv("MONGODB_URI","mongodb://localhost:27017/"),
                         serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = ensure_schema(client["crop_yield_db"])
        item = {"_id":"ca2-demo-"+uuid4().hex,
                "State_Name":"Demo State","District_Name":"Demo District",
                "Crop_Year":2026,"Season":"Kharif","Crop":"Demo Wheat",
                "Area":5.0,"Production":20.0,"Yield":4.0}
        try:
            print("CREATE:",collection.insert_one(item).inserted_id)
            print("READ:",collection.find_one({"_id":item["_id"]}))
            print("UPDATE:",collection.update_one({"_id":item["_id"]},
                  {"$set":{"Production":25.0,"Yield":5.0}}).modified_count)
            print("AFTER UPDATE:",collection.find_one({"_id":item["_id"]}))
            try:
                collection.update_one({"_id":item["_id"]},{"$set":{"Area":-1}})
            except WriteError as exc:
                print("VALIDATION: negative area rejected; code",exc.code)
            else:
                raise AssertionError("MongoDB accepted an invalid negative area")
        finally:
            print("DELETE:",collection.delete_one({"_id":item["_id"]}).deleted_count)
    finally:
        client.close()

if __name__ == "__main__":
    main()
