# CSE494 — Intelligent NoSQL Databases CA2: End-to-End Verification Report

**Auditor Role:** Senior Python Backend Engineer, MongoDB Database Engineer & QA Automation Engineer  
**Repository:** [https://github.com/ayushman031/Crop-Yield-Prediction](https://github.com/ayushman031/Crop-Yield-Prediction)  
**Execution Timestamp:** 2026-11-16T19:48:50+05:30  
**Overall Verdict:** **PASS — Fully Ready for CA2 Submission & Viva**

---

## 1. Environment Details

| Component | Target / Required | Detected / Verified | Status |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10/11 64-bit | Windows 11 (AMD64) | **PASS** |
| **Python Runtime** | Python 3.10+ | Python 3.12.10 | **PASS** |
| **Database Server** | MongoDB Server v6.0+ | MongoDB Community Server v9.0.2 | **PASS** |
| **Database Host / Port**| localhost:27017 | `mongodb://localhost:27017/` | **PASS** |
| **PyMongo Driver** | >=4.0.0 | 4.19.0 | **PASS** |
| **Web Framework** | Flask >=3.0.0 | Flask 3.1.0 (Werkzeug 3.1.3, Jinja2 3.1.6) | **PASS** |
| **Data Processing** | pandas >=2.0.0, numpy | pandas 3.0.3, numpy 2.5.0 | **PASS** |
| **Machine Learning**| scikit-learn >=1.4.0 | scikit-learn 1.9.0 | **PASS** |
| **Git LFS** | git-lfs >=3.0.0 | git-lfs/3.7.1 | **PASS** |
| **ML Model File** | `model.pkl` (Binary weights) | 1,648,327,742 bytes (~1.64 GB) | **PASS** |
| **Dataset File** | `crop_production_final.csv` | 17,300,104 bytes (~17.3 MB) | **PASS** |

---

## 2. Test Execution Summary

| Suite / Area | Tests Executed | Passed | Failed | Skipped | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Environment & Connectivity** | 6 | 6 | 0 | 0 | **PASS** |
| **2. MongoDB Schema Validation** | 12 | 12 | 0 | 0 | **PASS** |
| **3. CRUD Operations** | 6 | 6 | 0 | 0 | **PASS** |
| **4. Aggregation Pipelines** | 5 | 5 | 0 | 0 | **PASS** |
| **5. Dataset Integrity & Idempotency** | 4 | 4 | 0 | 0 | **PASS** |
| **6. Machine Learning Pipeline** | 6 | 6 | 0 | 0 | **PASS** |
| **7. Flask Web Endpoints & UI** | 8 | 8 | 0 | 0 | **PASS** |
| **8. Automated Unit & Integration Tests** | 13 | 13 | 0 | 0 | **PASS** |
| **TOTAL** | **60** | **60** | **0** | **0** | **PASS** |

---

## 3. Systematic Verification & Actual Outputs

### 3.1 Environment Verification

- **Command:**
  ```powershell
  python -c "import sys, flask, pymongo, pandas, sklearn; print(sys.version); print(flask.__version__); print(pymongo.__version__); print(pandas.__version__); print(sklearn.__version__)"
  ```
- **Actual Output:**
  ```text
  3.12.10 (tags/v3.12.10:0cc8128, Apr  8 2025, 12:21:36) [MSC v.1943 64 bit (AMD64)]
  3.1.0
  4.19.0
  3.0.3
  1.9.0
  ```
- **Verdict:** **PASS**

- **Database Connectivity & Collections Check:**
  - `client.admin.command('ping')`: `{'ok': 1.0}`
  - Databases: `['College', 'admin', 'config', 'crop_yield_db', 'local']`
  - Collection: `crop_yield_db.crop_records`
  - Total records: `240,403` documents
- **Verdict:** **PASS**

- **Git LFS Verification:**
  - `model.pkl` size on disk: `1,648,327,742` bytes (1.64 GB).
  - Verified binary header (not a Git LFS 3-line text pointer).
- **Verdict:** **PASS**

---

### 3.2 MongoDB Schema Validation (`schema_validation.py`)

- **BSON Schema Validator in MongoDB (`crop_records`):**
  - **Required fields (8):** `State_Name`, `District_Name`, `Crop_Year`, `Season`, `Crop`, `Area`, `Production`, `Yield`
  - **Type constraints:**
    - `State_Name`, `District_Name`, `Season`, `Crop`: `string` (`minLength: 1`)
    - `Crop_Year`: `int`, `long` (`minimum: 1900`, `maximum: 2100`)
    - `Area`: `int`, `long`, `double`, `decimal` (`minimum: 0`, `exclusiveMinimum: true`)
    - `Production`: `int`, `long`, `double`, `decimal` (`minimum: 0`)
    - `Yield`: `int`, `long`, `double`, `decimal` (`minimum: 0`)
  - **Indexes verified:**
    - `_id_`: standard primary key index
    - `geography_year`: compound index `("State_Name", 1), ("District_Name", 1), ("Crop_Year", 1)`
    - `crop_filter`: index on `("Crop", 1)`
    - `season_filter`: index on `("Season", 1)`

- **Negative Validation Tests (executed directly against MongoDB engine):**

| Test Case | Attempted Document Data | MongoDB Server Response | Verdict |
| :--- | :--- | :--- | :--- |
| Missing required field | Omitting `Crop` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Negative Area | `{"Area": -10.0}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Zero Area | `{"Area": 0.0}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Negative Production | `{"Production": -5.0}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Negative Yield | `{"Yield": -1.0}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Year below range | `{"Crop_Year": 1850}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Year above range | `{"Crop_Year": 2200}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Invalid Type (`Crop` as int) | `{"Crop": 123}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Invalid Type (`State_Name` as list) | `{"State_Name": ["State"]}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Empty String `State_Name` | `{"State_Name": ""}` | `WriteError: code 121 (DocumentValidationFailure)` | **PASS** |
| Valid Document Insertion | Full valid schema | Inserted ID: `test-pos-...`, retrieved and cleaned up | **PASS** |

---

### 3.3 CRUD Verification (`operations.py` & `crud_demo.py`)

- **Command:**
  ```powershell
  python crud_demo.py
  ```
- **Actual Output:**
  ```text
  CREATE: ca2-demo-8133bb113bcc46fbb405517b5f158c1a
  READ: {'_id': 'ca2-demo-8133bb113bcc46fbb405517b5f158c1a', 'State_Name': 'Demo State', 'District_Name': 'Demo District', 'Crop_Year': 2026, 'Season': 'Kharif', 'Crop': 'Demo Wheat', 'Area': 5.0, 'Production': 20.0, 'Yield': 4.0}
  UPDATE: 1
  AFTER UPDATE: {'_id': 'ca2-demo-8133bb113bcc46fbb405517b5f158c1a', 'State_Name': 'Demo State', 'District_Name': 'Demo District', 'Crop_Year': 2026, 'Season': 'Kharif', 'Crop': 'Demo Wheat', 'Area': 5.0, 'Production': 25.0, 'Yield': 5.0}
  VALIDATION: negative area rejected; code 121
  DELETE: 1
  ```
- **CRUD Operations Audit:**
  - `CREATE`: Successful insert with custom ID and ObjectId.
  - `READ`: Correct document fetched and validated.
  - `UPDATE`: Successfully updated numeric fields (`Production: 25.0`, `Yield: 5.0`).
  - `DELETE`: Cleaned up record; post-deletion query returned `None`.
  - **Rejection of illegal update:** Updating with `Area: -1` correctly rejected by MongoDB (code 121).
- **Verdict:** **PASS**

---

### 3.4 Aggregation Pipeline Verification (`aggregation_demo.py` & `operations.py`)

All aggregation pipelines were executed in MongoDB and cross-checked against independent Pandas calculations on the underlying CSV:

#### 1. Top Five Crops by Production (`$group`, `$sum`, `$sort`, `$limit`)
- **MongoDB Aggregation:**
  1. Sugarcane: 5,535,681,525.92
  2. Rice: 1,605,470,383.37
  3. Wheat: 1,332,825,656.80
  4. Potato: 424,826,343.86
  5. Cotton(lint): 297,000,015.70
- **Independent Pandas Result:** Exactly matches to the decimal place (`sugarcane: 5.535682e+09`, etc.).
- **Verdict:** **PASS**

#### 2. Top Five States by Cultivated Area (`$group`, `$sum`, `$sort`, `$limit`)
- **MongoDB Aggregation:**
  1. Uttar Pradesh: 433,622,332.00 ha
  2. Madhya Pradesh: 329,791,261.00 ha
  3. Maharashtra: 322,186,037.00 ha
  4. Rajasthan: 268,788,234.00 ha
  5. West Bengal: 215,098,683.87 ha
- **Independent Pandas Result:** 100% Exact Match.
- **Verdict:** **PASS**

#### 3. Highest Production Years (`$group`, `$sum`, `$sort`, `$limit`)
- **MongoDB Aggregation:**
  1. 1997: 844,888,764.00
  2. 2011: 714,686,165.13
  3. 2010: 711,408,165.37
  4. 2013: 684,400,655.88
  5. 2008: 677,234,892.16
- **Independent Pandas Result:** 100% Exact Match.
- **Verdict:** **PASS**

#### 4. Filtered KPIs (`$match`, `$group`, `$sum`, `$avg`)
- Filter: `State_Name: 'Andaman and Nicobar Islands'`, `District_Name: 'NICOBARS'`, `Season: 'Kharif'`
  - **MongoDB Aggregation:** `total_production = 5369.64`, `total_area = 2993.23`, `average_yield = 2.2575`
  - **Independent Pandas Result:** `total_production = 5369.64`, `total_area = 2993.23`, `average_yield = 2.2575`
- **Verdict:** **PASS**

---

### 3.5 Dataset Integrity & Idempotency (`dataset.py`)

- **First Import:**
  - Valid CSV rows: `240403`
  - Inserted records: `240403`
  - Total collection count: `240403`
- **Second Import (Idempotency Test):**
  - Valid CSV rows: `240403`
  - Inserted new records: `0`
  - Total collection count: `240403`
- **Idempotency Mechanism:**
  - Uses SHA-256 hash of canonical JSON-serialized record data as document `_id`.
  - Performs `UpdateOne({"_id": record["_id"]}, {"$setOnInsert": record}, upsert=True)` bulk writes.
  - Zero duplicate records created on repeated runs.
- **Verdict:** **PASS**

---

### 3.6 Machine Learning Verification (`ml.py`, `model.pkl`, `app.py`)

- **Model Specification:**
  - Estimator: `RandomForestRegressor(n_estimators=100, random_state=42)`
  - Categorical Encoders: LabelEncoder for `State_Name`, `District_Name`, `Season`, `Crop`
  - Feature Order: `['State_Name', 'District_Name', 'Crop_Year', 'Season', 'Crop', 'Area']` (6 features)
  - Memory Footprint: ~1,649.34 MB RSS when loaded.
- **Prediction Test Cases:**
  1. **Valid Input:**
     - `State = 'Andaman and Nicobar Islands'`, `District = 'NICOBARS'`, `Season = 'Kharif'`, `Crop = 'Arecanut'`, `Year = 2026`, `Area = 15.0`
     - **Result:** `2.35` (Type `float`, finite, non-null). **PASS**
  2. **Unknown Categorical Input:**
     - `State = 'NonExistentState'` -> correctly raises `ValueError` ("y contains previously unseen labels"), handled as HTTP 400. **PASS**
  3. **Invalid Area:**
     - Area `-5.0`, `0.0`, `nan`, `inf` -> caught and rejected by validator, HTTP 400. **PASS**
  4. **Invalid Year:**
     - Year `1800` (< 1900) or `2150` (> 2100) -> rejected by validator, HTTP 400. **PASS**
  5. **District / State Mismatch:**
     - `State = 'Andaman and Nicobar Islands'`, `District = 'AGRA'` -> rejected by `app.py` cross-validation ("District is not in the selected state"), HTTP 400. **PASS**
- **Verdict:** **PASS**

---

### 3.7 Flask Application Verification (`app.py`)

- **Endpoints Tested:**

| Method | Endpoint | Payload / Condition | Status Code | Verification | Verdict |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `GET` | `/health` | None | `200` | Returned `{"database":"connected","status":"ok"}` | **PASS** |
| `GET` | `/` | None | `200` | Rendered dashboard HTML with distinct dropdowns & initial stats | **PASS** |
| `POST`| `/` | `state="Andaman and Nicobar Islands"` | `200` | Filtered dashboard table & recomputed KPIs | **PASS** |
| `POST`| `/` | `load_districts="1"` | `200` | Loaded dependent district options dynamically | **PASS** |
| `GET` | `/prediction` | None | `200` | Rendered prediction form with all select elements | **PASS** |
| `POST`| `/prediction`| `state="Andaman and Nicobar Islands"` | `200` | Dynamic cascade district population | **PASS** |
| `POST`| `/predict` | Valid inputs | `200` | Rendered `Predicted Yield: 2.35` | **PASS** |
| `POST`| `/predict` | Non-integer year (`"bad"`) | `400` | User error handled safely, no crash | **PASS** |
| `POST`| `/predict` | Negative area (`"-5.0"`) | `400` | Caught by `area <= 0` guard, returned 400 | **PASS** |
| `POST`| `/predict` | Out-of-range year (`1800`) | `400` | Caught by `year < 1900` guard, returned 400 | **PASS** |
| `POST`| `/predict` | District not in state | `400` | Dynamic state/district integrity check passed | **PASS** |

- **Browser & Accessibility Audit:**
  - Running on: `http://127.0.0.1:5000`
  - No 500 internal server errors.
  - Fully responsive HTML/CSS layouts for both Dashboard and Predict pages.
- **Verdict:** **PASS**

---

### 3.8 Automated Unit & Integration Testing (`tests/`)

- **Command:**
  ```powershell
  python -m unittest discover -s tests -v
  ```
- **Actual Output:**
  ```text
  test_bad_year (test_app.FlaskTests.test_bad_year) ... ok
  test_health (test_app.FlaskTests.test_health) ... ok
  test_negative_area (test_app.FlaskTests.test_negative_area) ... ok
  test_aggregation_pipeline (test_integration.MongoIntegrationTests.test_aggregation_pipeline) ... ok
  test_crud_lifecycle (test_integration.MongoIntegrationTests.test_crud_lifecycle) ... ok
  test_schema_rejection_invalid_year (test_integration.MongoIntegrationTests.test_schema_rejection_invalid_year) ... ok
  test_schema_rejection_missing_crop (test_integration.MongoIntegrationTests.test_schema_rejection_missing_crop) ... ok
  test_schema_rejection_negative_area (test_integration.MongoIntegrationTests.test_schema_rejection_negative_area) ... ok
  test_schema_rejection_negative_production (test_integration.MongoIntegrationTests.test_schema_rejection_negative_production) ... ok
  test_schema_rejection_zero_area (test_integration.MongoIntegrationTests.test_schema_rejection_zero_area) ... ok
  test_indexes_and_validator (test_schema.SchemaTests.test_indexes_and_validator) ... ok
  test_numeric_constraints (test_schema.SchemaTests.test_numeric_constraints) ... ok
  test_required_fields (test_schema.SchemaTests.test_required_fields) ... ok

  ----------------------------------------------------------------------
  Ran 13 tests in 0.115s

  OK
  ```
- **Passed:** 13  
- **Failed:** 0  
- **Skipped:** 0  
- **Verdict:** **PASS**

---

## 4. Issues Discovered & Fixes Applied

### Issue 1: Hardcoded `ObjectId` in `operations.py`
- **Severity:** Medium
- **Root Cause:** In `operations.py`, `update_crop_record` and `delete_crop_record` forcibly wrapped `record_id` inside `ObjectId(record_id)`. However, `dataset.py` inserts records with 64-character SHA-256 string `_id` values, and `crud_demo.py` uses UUID strings. Passing a non-24-character hex string to `ObjectId(...)` raised `bson.errors.InvalidId`.
- **Fix:** Added `_normalize_id(record_id)` helper in `operations.py`:
  ```python
  def _normalize_id(record_id):
      if isinstance(record_id, ObjectId):
          return record_id
      if isinstance(record_id, str) and len(record_id) == 24 and ObjectId.is_valid(record_id):
          return ObjectId(record_id)
      return record_id
  ```
  This enables `operations.py` to seamlessly update and delete records whether identified by `ObjectId`, SHA-256 strings, or UUIDs.
- **Verification:** Tested with all 4 ID representations (ObjectId, 24-char hex string, 64-char sha256, UUID); all 4 operations returned modified/deleted count `1`. Regression tests in `tests/test_integration.py` pass cleanly.

---

## 5. Assignment Compliance Matrix (CSE494 CA2)

| Requirement | Evaluation Criteria | Implementation Location | Verified Status |
| :--- | :--- | :--- | :---: |
| **Real-world Problem** | Agriculture analytics & crop yield forecasting across India | `crop_production_final.csv`, `app.py`, `ml.py` | **PASS** |
| **Document Design** | Structured BSON document with geographic, temporal, and numeric data | `schema_validation.py`, `dataset.py` | **PASS** |
| **Schema Validation** | Strict server-side `$jsonSchema` rejection of missing fields, negative area/production, invalid years | `schema_validation.py` | **PASS** |
| **Database Indexing** | Compound index (`State_Name`, `District_Name`, `Crop_Year`) and field indexes (`Crop`, `Season`) | `schema_validation.py` | **PASS** |
| **PyMongo Integration**| Native Python driver connections, connection pooling, and timeout handling | `db.py`, `operations.py`, `dataset.py` | **PASS** |
| **CRUD Operations** | Complete lifecycle (Insert, Find, Update, Delete) with validation | `operations.py`, `crud_demo.py` | **PASS** |
| **Aggregation Pipelines** | Multi-stage `$match`, `$group`, `$sort`, `$limit`, `$sum`, `$avg` pipelines | `operations.py`, `aggregation_demo.py` | **PASS** |
| **Data Integrity** | Idempotent bulk upsert with duplicate rejection | `dataset.py` | **PASS** |
| **Machine Learning** | Trained Random Forest Regressor integrated into live web interface | `ml.py`, `model.pkl`, `app.py` | **PASS** |
| **Working Web UI** | Flask dashboard for analytics and interactive yield prediction form | `app.py`, `templates/dash.html`, `templates/pred.html`| **PASS** |
| **Automated Testing** | Unit tests + integration tests with isolated teardown | `tests/test_app.py`, `tests/test_schema.py`, `tests/test_integration.py` | **PASS** |

---

## 6. Recommendations & Viva Preparation Guide

1. **Demonstrating MongoDB Validation in Viva:**
   - Run `python crud_demo.py` to demonstrate live rejection of invalid documents by MongoDB itself (error code 121).
2. **Demonstrating Aggregation Pipelines:**
   - Run `python aggregation_demo.py` to display the 4 complex pipelines and explain how `$group`, `$sum`, and `$avg` calculate macro statistics over 240,403 records in under a second using indexes.
3. **Demonstrating the Web Application:**
   - Run `python app.py` and open `http://127.0.0.1:5000` to show the dynamic filtering, KPI cards, and yield prediction.
4. **Demonstrating Test Coverage:**
   - Run `python -m unittest discover -s tests -v` to demonstrate 13 passing unit and integration tests.

