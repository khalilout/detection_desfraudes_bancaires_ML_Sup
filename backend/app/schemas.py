"""
Schémas Pydantic pour l'API de détection de fraude.
"""
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """
    Une transaction à évaluer. Reprend exactement les colonnes du dataset
    Kaggle Credit Card Fraud (ULB) : Time, V1-V28 (composantes PCA), Amount.
    """
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float = Field(..., ge=0, description="Montant de la transaction en euros")


class PredictionResponse(BaseModel):
    is_fraud: bool
    fraud_probability: float
    decision_threshold: float


class BatchPredictionResponse(BaseModel):
    n_transactions: int
    n_predicted_fraud: int
    predictions: list[PredictionResponse]


class ModelInfoResponse(BaseModel):
    model_type: str
    decision_threshold: float
    n_features: int