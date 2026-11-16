from db import crop_collection
from bson import ObjectId
def count_crop_records():
    return crop_collection.count_documents({})

def get_crop_records():
    return list(crop_collection.find({}, {"_id": 0}).limit(5))

def filter_crop_records(crop=None, state=None, district=None,
                        season=None, year=None):
    query = {}
    if crop:
        query["Crop"] = crop
    if state:
        query["State_Name"] = state
    if district:
        query["District_Name"] = district
    if season:
        query["Season"] = season
    if year:
        query["Crop_Year"] = int(year)
    return list(crop_collection.find(query, {"_id": 0}).limit(100))

def get_distinct_values(field):
    return sorted(crop_collection.distinct(field), key=str)

def get_dashboard_stats():
    return {
        "total_records": count_crop_records(),
        "total_states": len(get_distinct_values("State_Name")),
        "total_districts": len(get_distinct_values("District_Name")),
        "total_crops": len(get_distinct_values("Crop"))}

def get_crop_kpis(state=None, district=None, season=None,
                  crop=None, year=None):
    query = {}
    if state:
        query["State_Name"] = state
    if district:
        query["District_Name"] = district
    if season:
        query["Season"] = season
    if crop:
        query["Crop"] = crop
    if year:
        query["Crop_Year"] = int(year)
    summary = list(crop_collection.aggregate([
        {"$match": query},
        {"$group": {
            "_id": None,"total_production": {"$sum": "$Production"},
            "total_area": {"$sum": "$Area"},"average_yield": {"$avg": "$Yield"}
        }}
    ]))
    if summary:
        summary = summary[0]
    else:
        summary = {"total_production": 0,"total_area": 0,"average_yield": 0
        }
    crop_stats = list(crop_collection.aggregate([
        {"$match": query},
        {"$group": {
            "_id": "$Crop","average_yield": {"$avg": "$Yield"},
            "total_production": {"$sum": "$Production"},
            "total_area": {"$sum": "$Area"}
        }}
    ]))
    if crop_stats:
        best_crop = max(crop_stats, key=lambda item: item["average_yield"])
        worst_crop = min(crop_stats, key=lambda item: item["average_yield"])
        most_cultivated_crop = max(crop_stats, key=lambda item: item["total_area"])
    else:
        best_crop = None
        worst_crop = None
        most_cultivated_crop = None
    historical_query = query.copy()
    historical_query.pop("Crop_Year", None)
    yearly_stats = list(crop_collection.aggregate([
        {"$match": historical_query},
        {"$group": {"_id": "$Crop_Year","total_production": {"$sum": "$Production"}}},
        {"$sort": {"total_production": -1}},
        {"$limit": 1}]))
    best_year = yearly_stats[0] if yearly_stats else None
    return {
        "total_production": summary["total_production"],
        "total_area": summary["total_area"],
        "average_yield": summary["average_yield"],
        "best_crop": best_crop,
        "worst_crop": worst_crop,
        "most_cultivated_crop": most_cultivated_crop,
        "best_year": best_year}

def add_crop_record(record):
    result = crop_collection.insert_one(record)
    return result.inserted_id

def update_crop_record(record_id, updates):
    result = crop_collection.update_one({"_id": ObjectId(record_id)},{"$set": updates})
    return result.modified_count

def create_crop_index():
    return crop_collection.create_index("Crop")

def create_crop_filter_index():
    return crop_collection.create_index([("State_Name", 1),("District_Name", 1),("Crop_Year", 1)])

def delete_crop_record(record_id):
    result = crop_collection.delete_one({"_id": ObjectId(record_id)})
    return result.deleted_count