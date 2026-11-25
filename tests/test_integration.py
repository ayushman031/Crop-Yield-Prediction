"""Integration tests executed against an isolated MongoDB test database."""
import os
import unittest
from uuid import uuid4
from pymongo import MongoClient
from pymongo.errors import WriteError
from schema_validation import ensure_schema

TEST_DB_NAME = "crop_yield_test_db"

class MongoIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        cls.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        try:
            cls.client.admin.command("ping")
        except Exception:
            raise unittest.SkipTest("MongoDB server not reachable; skipping integration tests.")
        cls.db = cls.client[TEST_DB_NAME]
        cls.collection = ensure_schema(cls.db)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "client") and hasattr(cls, "db"):
            cls.client.drop_database(TEST_DB_NAME)
            cls.client.close()

    def test_crud_lifecycle(self):
        doc_id = "test-crud-" + uuid4().hex
        doc = {
            "_id": doc_id,
            "State_Name": "Integration State",
            "District_Name": "Integration District",
            "Crop_Year": 2026,
            "Season": "Kharif",
            "Crop": "Rice",
            "Area": 12.0,
            "Production": 60.0,
            "Yield": 5.0
        }
        # Create
        res = self.collection.insert_one(doc)
        self.assertEqual(res.inserted_id, doc_id)

        # Read
        found = self.collection.find_one({"_id": doc_id})
        self.assertIsNotNone(found)
        self.assertEqual(found["Crop"], "Rice")

        # Update
        mod = self.collection.update_one({"_id": doc_id}, {"$set": {"Production": 72.0, "Yield": 6.0}})
        self.assertEqual(mod.modified_count, 1)
        after = self.collection.find_one({"_id": doc_id})
        self.assertEqual(after["Production"], 72.0)

        # Delete
        deleted = self.collection.delete_one({"_id": doc_id})
        self.assertEqual(deleted.deleted_count, 1)
        self.assertIsNone(self.collection.find_one({"_id": doc_id}))

    def test_schema_rejection_negative_area(self):
        doc = {
            "_id": "bad-area-" + uuid4().hex,
            "State_Name": "S", "District_Name": "D", "Crop_Year": 2026,
            "Season": "Kharif", "Crop": "Rice",
            "Area": -5.0, "Production": 10.0, "Yield": 2.0
        }
        with self.assertRaises(WriteError):
            self.collection.insert_one(doc)

    def test_schema_rejection_zero_area(self):
        doc = {
            "_id": "bad-zero-area-" + uuid4().hex,
            "State_Name": "S", "District_Name": "D", "Crop_Year": 2026,
            "Season": "Kharif", "Crop": "Rice",
            "Area": 0.0, "Production": 10.0, "Yield": 2.0
        }
        with self.assertRaises(WriteError):
            self.collection.insert_one(doc)

    def test_schema_rejection_negative_production(self):
        doc = {
            "_id": "bad-prod-" + uuid4().hex,
            "State_Name": "S", "District_Name": "D", "Crop_Year": 2026,
            "Season": "Kharif", "Crop": "Rice",
            "Area": 5.0, "Production": -10.0, "Yield": 2.0
        }
        with self.assertRaises(WriteError):
            self.collection.insert_one(doc)

    def test_schema_rejection_missing_crop(self):
        doc = {
            "_id": "bad-missing-" + uuid4().hex,
            "State_Name": "S", "District_Name": "D", "Crop_Year": 2026,
            "Season": "Kharif",
            "Area": 5.0, "Production": 10.0, "Yield": 2.0
        }
        with self.assertRaises(WriteError):
            self.collection.insert_one(doc)

    def test_schema_rejection_invalid_year(self):
        doc = {
            "_id": "bad-year-" + uuid4().hex,
            "State_Name": "S", "District_Name": "D", "Crop_Year": 1800,
            "Season": "Kharif", "Crop": "Rice",
            "Area": 5.0, "Production": 10.0, "Yield": 2.0
        }
        with self.assertRaises(WriteError):
            self.collection.insert_one(doc)

    def test_aggregation_pipeline(self):
        sample_records = [
            {"_id": "agg-1", "State_Name": "StateA", "District_Name": "Dist1", "Crop_Year": 2020, "Season": "Kharif", "Crop": "Rice", "Area": 10.0, "Production": 50.0, "Yield": 5.0},
            {"_id": "agg-2", "State_Name": "StateA", "District_Name": "Dist1", "Crop_Year": 2020, "Season": "Rabi", "Crop": "Wheat", "Area": 20.0, "Production": 80.0, "Yield": 4.0},
            {"_id": "agg-3", "State_Name": "StateB", "District_Name": "Dist2", "Crop_Year": 2021, "Season": "Kharif", "Crop": "Rice", "Area": 15.0, "Production": 90.0, "Yield": 6.0},
        ]
        self.collection.insert_many(sample_records)
        try:
            # Aggregate total production by Crop
            res = list(self.collection.aggregate([
                {"$group": {"_id": "$Crop", "total": {"$sum": "$Production"}}},
                {"$sort": {"total": -1}}
            ]))
            self.assertEqual(res[0]["_id"], "Rice")
            self.assertEqual(res[0]["total"], 140.0)
            self.assertEqual(res[1]["_id"], "Wheat")
            self.assertEqual(res[1]["total"], 80.0)
        finally:
            self.collection.delete_many({"_id": {"$in": ["agg-1", "agg-2", "agg-3"]}})

if __name__ == "__main__":
    unittest.main()

