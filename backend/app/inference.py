"""
Module d'inférence — charge le modèle XGBoost entraîné (voir notebooks/) et
ses artefacts (scalers, seuil de décision), et expose une fonction de prédiction.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"


class FraudDetector:
    def __init__(self, models_dir: Path = MODELS_DIR):
        self.model = joblib.load(models_dir / "fraud_model.joblib")
        self.scaler_amount = joblib.load(models_dir / "scaler_amount.joblib")
        self.scaler_time = joblib.load(models_dir / "scaler_time.joblib")

        with open(models_dir / "model_config.json") as f:
            self.config = json.load(f)

        self.feature_order: list[str] = self.config["feature_order"]
        self.decision_threshold: float = self.config["decision_threshold"]
        self.model_type: str = self.config["model_type"]

    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applique le même scaling que celui appris lors de l'entraînement."""
        df = df.copy()
        df["Amount"] = self.scaler_amount.transform(df[["Amount"]])
        df["Time"] = self.scaler_time.transform(df[["Time"]])
        return df[self.feature_order]

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        prepared = self._prepare(df)
        return self.model.predict_proba(prepared)[:, 1]

    def predict(self, df: pd.DataFrame) -> list[dict]:
        """Renvoie, pour chaque ligne, la probabilité de fraude et la décision finale."""
        probabilities = self.predict_proba(df)
        return [
            {
                "is_fraud": bool(p >= self.decision_threshold),
                "fraud_probability": float(round(p, 6)),
                "decision_threshold": self.decision_threshold,
            }
            for p in probabilities
        ]


detector = FraudDetector()