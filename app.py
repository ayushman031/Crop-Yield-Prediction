from flask import Flask, render_template, request
from db import crop_collection
from operations import (
    get_distinct_values,
    get_dashboard_stats,
    filter_crop_records,
    get_crop_kpis
)
import pandas as pd
import pickle

app = Flask(__name__)

with open("model.pkl", "rb") as file:
    model, encoders = pickle.load(file)

def get_dropdowns(state=""):
    if state:
        districts = sorted(
            crop_collection.distinct("District_Name", {"State_Name": state}),key=str)
    else:
        districts = get_distinct_values("District_Name")
    return {
        "states": get_distinct_values("State_Name"),"districts": districts,
        "crops": get_distinct_values("Crop"),"seasons": get_distinct_values("Season")}

@app.route("/", methods=["GET", "POST"])
def home():
    state = request.form.get("state", "")
    district = request.form.get("district", "")
    crop = request.form.get("crop", "")
    season = request.form.get("season", "")
    year = request.form.get("year", "")

    if request.form.get("load_districts"):
        district = crop = season = year = ""
    records = filter_crop_records(
        crop=crop, state=state, district=district, season=season, year=year)
    kpis = get_crop_kpis(state=state, district=district,season=season, crop=crop, year=year)

    return render_template(
        "dash.html",
        **get_dropdowns(state),
        years=sorted(get_distinct_values("Crop_Year")),
        selected_state=state,
        selected_district=district,
        selected_crop=crop,
        selected_season=season,
        selected_year=year,
        records=records,
        stats=get_dashboard_stats(),
        kpis=kpis
    )

@app.route("/prediction", methods=["GET", "POST"])
def prediction_page():
    state = request.form.get("state", "")
    return render_template("pred.html",
        **get_dropdowns(state),selected_state=state, selected_district="", selected_crop="", selected_season="", selected_year="", selected_area="")

@app.route("/predict", methods=["POST"])
def predict():
    state = request.form["state"]
    district = request.form["district"]
    season = request.form["season"]
    crop = request.form["crop"]
    year = int(request.form["year"])
    area = float(request.form["area"])

    values = {column: encoders[column].transform([value.strip()])[0]
        for column, value in {"State_Name": state, "District_Name": district, "Season": season, "Crop": crop}.items()}

    data = pd.DataFrame([{"State_Name": values["State_Name"],"District_Name": values["District_Name"],"Crop_Year": year,
        "Season": values["Season"],"Crop": values["Crop"],"Area": area}])

    prediction = round(float(model.predict(data)[0]), 2)

    return render_template(
        "pred.html",
        **get_dropdowns(state),
        selected_state=state,
        selected_district=district,
        selected_crop=crop,
        selected_season=season,
        selected_year=year,
        selected_area=area,
        prediction=prediction
    )
if __name__ == "__main__":
    app.run(debug=True)
