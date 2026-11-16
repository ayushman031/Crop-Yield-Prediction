"""Idempotent crop CSV import; run with python dataset.py."""
import hashlib
import json
import os
import pandas as pd
from pymongo import MongoClient, UpdateOne
from schema_validation import ensure_schema

FIELDS = ["State_Name","District_Name","Crop_Year","Season","Crop","Area","Production","Yield"]

def records_from_csv(path):
    df = pd.read_csv(path,usecols=FIELDS)
    for field in ("State_Name","District_Name","Season","Crop"):
        df[field] = df[field].astype("string").str.strip()
        df.loc[df[field] == "",field] = pd.NA
    for field in ("Crop_Year","Area","Production","Yield"):
        df[field] = pd.to_numeric(df[field],errors="coerce")
    df = df.dropna(subset=FIELDS)
    df = df[(df.Crop_Year >= 1900) & (df.Crop_Year <= 2100) &
            (df.Crop_Year % 1 == 0) & (df.Area > 0) &
            (df.Production >= 0) & (df.Yield >= 0)]
    print("Valid CSV rows:",len(df))
    for row in df.to_dict("records"):
        record = {field:str(row[field]) for field in ("State_Name","District_Name","Season","Crop")}
        record.update(Crop_Year=int(row["Crop_Year"]),Area=float(row["Area"]),
                      Production=float(row["Production"]),Yield=float(row["Yield"]))
        serialized = json.dumps(record,sort_keys=True,allow_nan=False)
        record["_id"] = hashlib.sha256(serialized.encode()).hexdigest()
        yield record

def import_data(path=None):
    client = MongoClient(os.getenv("MONGODB_URI","mongodb://localhost:27017/"),
                         serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = ensure_schema(client["crop_yield_db"])
        path = path or os.getenv("CROP_CSV_PATH","crop_production_final.csv")
        pending = []
        inserted = 0
        for record in records_from_csv(path):
            pending.append(UpdateOne({"_id":record["_id"]},
                                     {"$setOnInsert":record},upsert=True))
            if len(pending) == 1000:
                inserted += collection.bulk_write(pending,ordered=False).upserted_count
                pending.clear()
        if pending:
            inserted += collection.bulk_write(pending,ordered=False).upserted_count
        print("Inserted new records:",inserted)
        print("Total records:",collection.count_documents({}))
    finally:
        client.close()

if __name__ == "__main__":
    import_data()
