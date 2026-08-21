import os
from pathlib import Path

import boto3
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

S3_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = Path(
    os.getenv("MODEL_PATH", str(Path.home() / "models" / "model.pkl"))
)
EXPECTED_FEATURE_COUNT = 12
FEATURE_NAMES = [
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol",
    "wine_type",
]
LABELS = {0: "thap", 1: "trung_binh", 2: "cao"}

app = FastAPI(title="Wine Quality Classifier", version="1.0.0")
model = None


def download_model(
    bucket_name: str,
    model_key: str = S3_MODEL_KEY,
    destination: Path = MODEL_PATH,
) -> Path:
    """Download the currently deployed model from Amazon S3."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    boto3.client("s3").download_file(bucket_name, model_key, str(destination))
    print(f"Downloaded s3://{bucket_name}/{model_key} to {destination}.")
    return destination


@app.on_event("startup")
def load_model() -> None:
    """Refresh and load the model whenever the API service starts."""
    global model

    bucket_name = os.getenv("CLOUD_BUCKET")
    if bucket_name:
        download_model(bucket_name)
    elif not MODEL_PATH.exists():
        raise RuntimeError(
            "CLOUD_BUCKET is not configured and no local model exists at "
            f"{MODEL_PATH}."
        )

    model = joblib.load(MODEL_PATH)


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple liveness response used by the deploy job."""
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictRequest) -> dict[str, int | str]:
    """Predict one of the three wine-quality classes."""
    if len(request.features) != EXPECTED_FEATURE_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Expected {EXPECTED_FEATURE_COUNT} features.",
        )

    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    features = pd.DataFrame([request.features], columns=FEATURE_NAMES)
    prediction = int(model.predict(features)[0])
    return {
        "prediction": prediction,
        "label": LABELS.get(prediction, "khong_xac_dinh"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
