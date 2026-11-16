# NoSQL Crop Yield Analysis & Prediction Dashboard 🌾

An intelligent crop analytics and yield prediction system combining a **MongoDB** document database, **Flask** web application, and **Random Forest Machine Learning model** for historical analysis and yield forecasting across Indian states, districts, seasons, and crops.

---

## 🚀 Features

- **Interactive Analytics Dashboard**:
  - Filter historical crop yield and production records by State, District, Season, Crop, and Year.
  - Aggregated KPIs for total production, cultivated area, and average yield.
  - Identification of top-performing crops, most cultivated crops, and peak production years using MongoDB aggregation pipelines.

- **Machine Learning Yield Prediction**:
  - Predict expected crop yield using a trained Random Forest Regressor (`model.pkl`).
  - Encodes categorical geographic and seasonal inputs dynamically.

- **High-Performance Database**:
  - Backed by MongoDB with indexed queries on crop attributes and compound geographic/temporal keys.
  - Over 240,000+ historical records processed and indexed.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Flask
- **Database**: MongoDB (via `pymongo`)
- **Machine Learning & Data**: scikit-learn, pandas, numpy
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Large File Storage**: Git LFS (for `model.pkl`)

---

## 📦 Project Structure

```text
NoSQL-Crop-Yield-Analysis/
├── templates/
│   ├── dash.html                 # Analytics dashboard interface
│   └── pred.html                 # Yield prediction interface
├── app.py                        # Flask server & route controllers
├── dataset.py                    # ETL script to load CSV data into MongoDB
├── db.py                         # MongoDB connection & collection setup
├── ml.py                         # ML model training and evaluation script
├── operations.py                 # MongoDB query & aggregation functions
├── crop_production_final.csv     # Crop dataset (~240k records)
├── model.pkl                     # Serialized Random Forest model (Git LFS)
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

---

## ⚙️ Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **MongoDB Server** (running locally on port `27017`)
- **Git & Git LFS**

### 2. Clone Repository
```bash
git clone https://github.com/ayushman031/Crop-Yield-Prediction.git
cd Crop-Yield-Prediction
git lfs pull
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup MongoDB & Import Dataset
Ensure your MongoDB service is running on `mongodb://localhost:27017/`:
```bash
python dataset.py
```
*(Optional: verify indexes and operations by importing from `operations.py`)*

### 5. Train / Verify Model (Optional)
The pre-trained model is included via Git LFS. If you wish to retrain the model:
```bash
python ml.py
```

### 6. Run the Application
```bash
python app.py
```
Open your web browser and navigate to:
- **Dashboard**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Yield Prediction**: [http://127.0.0.1:5000/prediction](http://127.0.0.1:5000/prediction)

---

## 📄 License
This project is licensed under the MIT License.



## CA2 Assignment

See [README_CA2.md](README_CA2.md) for MongoDB validation, CRUD/aggregation demos, setup and viva instructions.
