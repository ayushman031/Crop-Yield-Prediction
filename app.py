"""Flask crop prediction and analytics UI."""
import math
import os
import pickle
from functools import lru_cache
import pandas as pd
from flask import Flask, render_template, request, jsonify
from pymongo.errors import PyMongoError
from db import client, crop_collection
from operations import get_distinct_values, get_dashboard_stats, filter_crop_records, get_crop_kpis

app = Flask(__name__)

@lru_cache(maxsize=1)
def get_model():
    with open(os.getenv("MODEL_PATH", "model.pkl"), "rb") as f:
        return pickle.load(f)

def get_dropdowns(state=""):
    districts = sorted(crop_collection.distinct("District_Name", {"State_Name":state}),key=str) if state else get_distinct_values("District_Name")
    return {"states":get_distinct_values("State_Name"), "districts":districts,
            "crops":get_distinct_values("Crop"),"seasons":get_distinct_values("Season")}

@app.get("/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify(status="ok",database="connected"),200
    except PyMongoError:
        return jsonify(status="unavailable",database="disconnected"),503

@app.route("/",methods=["GET","POST"])
def home():
    state=request.form.get("state","")
    district=request.form.get("district","")
    crop=request.form.get("crop","")
    season=request.form.get("season","")
    year=request.form.get("year","")
    if request.form.get("load_districts"):
        district=crop=season=year=""
    try:
        records=filter_crop_records(crop=crop,state=state,district=district,season=season,year=year)
        kpis=get_crop_kpis(state=state,district=district,season=season,crop=crop,year=year)
        return render_template("dash.html",**get_dropdowns(state),
            years=sorted(get_distinct_values("Crop_Year")),
            selected_state=state,selected_district=district,
            selected_crop=crop,selected_season=season,selected_year=year,
            records=records,stats=get_dashboard_stats(),kpis=kpis)
    except ValueError:
        return "Invalid filter value.",400
    except PyMongoError:
        return "MongoDB unavailable.",503

@app.route("/prediction",methods=["GET","POST"])
def prediction_page():
    state=request.form.get("state","")
    try:
        return render_template("pred.html",**get_dropdowns(state),selected_state=state,
            selected_district="",selected_crop="",selected_season="",selected_year="",selected_area="")
    except PyMongoError:
        return "MongoDB unavailable.",503

def render_prediction(state,district,season,crop,year,area,**extras):
    return render_template("pred.html",**get_dropdowns(state),
        selected_state=state,selected_district=district,selected_crop=crop,
        selected_season=season,selected_year=year,selected_area=area,**extras)

@app.post("/predict")
def predict():
    state=request.form.get("state","").strip()
    district=request.form.get("district","").strip()
    season=request.form.get("season","").strip()
    crop=request.form.get("crop","").strip()
    year_text=request.form.get("year","")
    area_text=request.form.get("area","")
    try:
        year=int(year_text)
        area=float(area_text)
        if year<1900 or year>2100 or not math.isfinite(area) or area<=0:
            raise ValueError("Use a valid year and a positive area.")
        if not all((state,district,season,crop)):
            raise ValueError("Select all location and crop fields.")
        if district not in crop_collection.distinct("District_Name",{"State_Name":state}):
            raise ValueError("District is not in the selected state.")
        model,encoders=get_model()
        raw={"State_Name":state,"District_Name":district,"Season":season,"Crop":crop}
        codes={k:encoders[k].transform([v])[0] for k,v in raw.items()}
        data=pd.DataFrame([{"State_Name":codes["State_Name"],"District_Name":codes["District_Name"],
            "Crop_Year":year,"Season":codes["Season"],"Crop":codes["Crop"],"Area":area}])
        result=float(model.predict(data)[0])
        if not math.isfinite(result):
            raise ValueError("Model returned an invalid prediction.")
        return render_prediction(state,district,season,crop,year,area,prediction=round(result,2))
    except (ValueError,KeyError) as exc:
        return render_prediction(state,district,season,crop,year_text,area_text,error=str(exc)),400
    except (FileNotFoundError,EOFError,pickle.UnpicklingError):
        return render_prediction(state,district,season,crop,year_text,area_text,
            error="Model not available. Run git lfs pull."),503
    except PyMongoError:
        return "MongoDB unavailable.",503

if __name__=="__main__":
    app.run(debug=os.getenv("FLASK_DEBUG")=="1")
