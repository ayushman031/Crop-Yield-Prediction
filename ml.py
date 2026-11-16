import pandas as pd
import pickle

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

df = pd.read_csv("crop_production_final.csv")
df = df[(df["Area"] > 0) & (df["Yield"] >= 0)]
encoders = {}

for column in ["State_Name", "District_Name", "Season", "Crop"]:
    encoders[column] = LabelEncoder()
    df[column] = encoders[column].fit_transform(df[column].astype(str))

features = [
    "State_Name", "District_Name", "Crop_Year",
    "Season", "Crop", "Area"
]

X = df[features]
y = df["Yield"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = RandomForestRegressor(n_estimators=100,random_state=42)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
print("MAE:", round(mean_absolute_error(y_test, predictions), 2))
print("MSE:", round(mean_squared_error(y_test, predictions), 2))
print("R2 Score:", round(r2_score(y_test, predictions), 4))

with open("model.pkl", "wb") as file:
    pickle.dump((model, encoders), file)
print("Model saved successfully!")

def predict_yield(state, district, year, season, crop, area):
    state = str(state)
    district = str(district)
    season = str(season)
    crop = str(crop)
    if state not in encoders["State_Name"].classes_:
        raise ValueError("State not found in the dataset.")
    if district not in encoders["District_Name"].classes_:
        raise ValueError("District not found in the dataset.")
    if season not in encoders["Season"].classes_:
        raise ValueError("Season not found in the dataset.")
    if crop not in encoders["Crop"].classes_:
        raise ValueError("Crop not found in the dataset.")
    
    state = encoders["State_Name"].transform([state])[0]
    district = encoders["District_Name"].transform([district])[0]
    season = encoders["Season"].transform([season])[0]
    crop = encoders["Crop"].transform([crop])[0]

    input_data = pd.DataFrame([{
        "State_Name": state,
        "District_Name": district,
        "Crop_Year": int(year),
        "Season": season,
        "Crop": crop,
        "Area": float(area)
    }])

    result = model.predict(input_data)[0]
    return round(float(result), 2)