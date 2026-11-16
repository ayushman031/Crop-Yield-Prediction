# CA2 MongoDB demonstration guide

Crop Yield Prediction applies MongoDB and PyMongo to historical agricultural
records in crop_yield_db.crop_records.

The dataset importer defines a document with state, district, year, season,
crop, area, production, and yield. MongoDB JSON Schema validates required fields,
types, and nonnegative numeric quantities, with area strictly positive.
Indexes support geographical, crop, and season filters. Import is repeat-safe
for identical normalized records.

## Setup

Prerequisites: Python 3.10+, MongoDB running locally on port 27017, Git LFS.
Optional environment variables: MONGODB_URI and MODEL_PATH.

1. git lfs pull
2. python -m pip install -r requirements.txt
3. python dataset.py
4. python crud_demo.py
5. python aggregation_demo.py
6. python -m unittest discover -s tests -v
7. python app.py

Dashboard: http://127.0.0.1:5000/
Prediction: http://127.0.0.1:5000/prediction
Health: http://127.0.0.1:5000/health

For the viva, show schema_validation.py for validator and indexes,
crud_demo.py for INSERT, FIND, UPDATE, DELETE, and invalid update rejection,
aggregation_demo.py for MATCH, GROUP, SORT, LIMIT, and the two Flask pages.

Important: The trained model is about 1.65 GB and must be retrieved through
Git LFS for predictions. The database dashboard loads without the model.
Capture screenshots of your real outputs and working pages after local execution.
A source-code commit alone does not verify the app runs with a live MongoDB server.
