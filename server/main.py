from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import pickle
import numpy as np
import json
import os

app = FastAPI(title="Bangalore House Price Prediction API")

# -----------------------------
# Load Model & Columns
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "model", "banglore_home_prices_model.pickle")
columns_path = os.path.join(BASE_DIR, "model", "columns.json")

# Load trained model
with open(model_path, "rb") as f:
    model = pickle.load(f)

# Load feature columns
with open(columns_path, "r") as f:
    data_columns = json.load(f)["data_columns"]

locations = data_columns[3:]   # first 3 columns are sqft, bath, bhk


# -----------------------------
# Request Body Schema
# -----------------------------

class HouseData(BaseModel):
    total_sqft: float
    bath: float
    bhk: int
    location: str


# -----------------------------
# Prediction Logic
# -----------------------------

def get_estimated_price(location: str, sqft: float, bath: float, bhk: int):

    # Create zero array of correct length
    x = np.zeros(len(data_columns))

    # Fill numeric features
    x[0] = sqft
    x[1] = bath
    x[2] = bhk

    # Set location one-hot encoding
    location = location.lower()
    if location in data_columns:
        loc_index = data_columns.index(location)
        x[loc_index] = 1
    else:
        # If location not found, raise proper error
        raise HTTPException(status_code=400, detail="Invalid location")

    # Predict
    prediction = model.predict([x])[0]

    return round(prediction, 2)


# -----------------------------
# API Endpoints
# -----------------------------




@app.get("/locations")
def get_locations():
    return {"locations": locations}


@app.post("/predict")
def predict_price(data: HouseData):

    price = get_estimated_price(
        data.location,
        data.total_sqft,
        data.bath,
        data.bhk
    )

    return {"estimated_price": price}

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "client")),
    name="static"
)

@app.get("/")
def serve_home():
    return FileResponse("../client/index.html")

