import pandas as pd

df = pd.read_csv("crop_production_final.csv")

print("Number of rows:", df.shape[0])
print("Number of columns:", df.shape[1])

print("\nColumn names:")
print(df.columns.tolist())

print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["crop_yield_db"]
collection = db["crop_records"]

records = df.to_dict("records")

collection.insert_many(records)

print("Dataset imported")
print("Total records:", collection.count_documents({}))