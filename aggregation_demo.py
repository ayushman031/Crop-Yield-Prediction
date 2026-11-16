"""Aggregation demonstrations for the CA2 viva."""
import os
from pprint import pprint
from pymongo import MongoClient

PIPELINES = {
    "Top five crops by production":[
        {"$group":{"_id":"$Crop","total":{"$sum":"$Production"}}},
        {"$sort":{"total":-1}},{"$limit":5}],
    "Top five states by cultivated area":[
        {"$group":{"_id":"$State_Name","total":{"$sum":"$Area"}}},
        {"$sort":{"total":-1}},{"$limit":5}],
    "Latest five years by production":[
        {"$group":{"_id":"$Crop_Year","total":{"$sum":"$Production"}}},
        {"$sort":{"_id":-1}},{"$limit":5}],
    "Top Kharif crops by average yield":[
        {"$match":{"Season":"Kharif"}},
        {"$group":{"_id":"$Crop","average_yield":{"$avg":"$Yield"}}},
        {"$sort":{"average_yield":-1}},{"$limit":5}]
}

def main():
    client = MongoClient(os.getenv("MONGODB_URI","mongodb://localhost:27017/"),
                         serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = client["crop_yield_db"]["crop_records"]
        if not collection.count_documents({}):
            raise RuntimeError("Database empty: run python dataset.py first")
        for title,pipeline in PIPELINES.items():
            print("\n"+title)
            pprint(list(collection.aggregate(pipeline)))
    finally:
        client.close()

if __name__ == "__main__":
    main()
