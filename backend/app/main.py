"""
API FastAPI — Détection de fraude par carte bancaire.
"""
import io

import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .inference import detector
from .schemas import Transaction, PredictionResponse, BatchPredictionResponse, ModelInfoResponse

app = FastAPI(
    title="Fraud Detection API",
    description="Détection de fraude par carte bancaire (dataset Kaggle Credit Card Fraud - ULB)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Fraud Detection API is running"}


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    return {
        "model_type": detector.model_type,
        "decision_threshold": detector.decision_threshold,
        "n_features": len(detector.feature_order),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_single(transaction: Transaction):
    df = pd.DataFrame([transaction.model_dump()])
    result = detector.predict(df)[0]
    return result


@app.post("/predict-batch", response_model=BatchPredictionResponse)
def predict_batch(file: UploadFile = File(...)):
    """
    Le CSV doit contenir exactement les colonnes : Time, V1...V28, Amount
    (les mêmes que le dataset d'entraînement, sans la colonne Class).
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers .csv sont acceptés.")

    content = file.file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Impossible de lire le CSV : {e}")

    missing_cols = set(detector.feature_order) - set(df.columns)
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail=f"Colonnes manquantes dans le CSV : {sorted(missing_cols)}",
        )

    predictions = detector.predict(df)
    n_fraud = sum(p["is_fraud"] for p in predictions)

    return {
        "n_transactions": len(predictions),
        "n_predicted_fraud": n_fraud,
        "predictions": predictions,
    }