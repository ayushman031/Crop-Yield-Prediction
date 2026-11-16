"""MongoDB server-side validation and indexes."""
from pymongo import ASCENDING
from pymongo.errors import CollectionInvalid

CROP_VALIDATOR = {"$jsonSchema": {
    "bsonType": "object",
    "required": ["State_Name","District_Name","Crop_Year","Season","Crop","Area","Production","Yield"],
    "properties": {
        "State_Name": {"bsonType":"string","minLength":1},
        "District_Name": {"bsonType":"string","minLength":1},
        "Season": {"bsonType":"string","minLength":1},
        "Crop": {"bsonType":"string","minLength":1},
        "Crop_Year": {"bsonType":["int","long"],"minimum":1900,"maximum":2100},
        "Area": {"bsonType":["int","long","double","decimal"],"minimum":0,"exclusiveMinimum":True},
        "Production": {"bsonType":["int","long","double","decimal"],"minimum":0},
        "Yield": {"bsonType":["int","long","double","decimal"],"minimum":0}
    }
}}

def ensure_schema(db):
    name = "crop_records"
    if name not in db.list_collection_names():
        try:
            db.create_collection(name,validator=CROP_VALIDATOR,
                                 validationLevel="strict",validationAction="error")
        except CollectionInvalid:
            pass
    db.command({"collMod":name,"validator":CROP_VALIDATOR,
                "validationLevel":"strict","validationAction":"error"})
    collection = db[name]
    collection.create_index([("State_Name",ASCENDING),("District_Name",ASCENDING),
                             ("Crop_Year",ASCENDING)],name="geography_year")
    collection.create_index("Crop",name="crop_filter")
    collection.create_index("Season",name="season_filter")
    return collection
