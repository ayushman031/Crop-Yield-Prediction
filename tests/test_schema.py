"""Unit tests that don't require a running MongoDB server."""
import unittest
from unittest.mock import MagicMock
from schema_validation import CROP_VALIDATOR,ensure_schema

class SchemaTests(unittest.TestCase):
    def test_required_fields(self):
        self.assertEqual(len(CROP_VALIDATOR["$jsonSchema"]["required"]),8)
    def test_numeric_constraints(self):
        fields=CROP_VALIDATOR["$jsonSchema"]["properties"]
        self.assertEqual(fields["Area"]["minimum"],0)
        self.assertIs(fields["Area"]["exclusiveMinimum"],True)
        self.assertEqual(fields["Production"]["minimum"],0)
    def test_indexes_and_validator(self):
        db=MagicMock()
        db.list_collection_names.return_value=[]
        coll=ensure_schema(db)
        db.create_collection.assert_called_once()
        db.command.assert_called_once()
        self.assertEqual(coll.create_index.call_count,3)

if __name__ == "__main__":
    unittest.main()
