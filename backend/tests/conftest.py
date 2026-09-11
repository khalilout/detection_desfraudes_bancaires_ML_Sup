"""Fixtures partagées entre les fichiers de test."""
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_transaction_dict() -> dict:
    """Une transaction valide, complète, prête à être envoyée à l'API."""
    rng = np.random.default_rng(42)
    return {
        "Time": 1000.0,
        "Amount": 50.0,
        **{f"V{i}": float(rng.normal(0, 1)) for i in range(1, 29)},
    }


@pytest.fixture
def sample_batch_df() -> pd.DataFrame:
    """Un petit lot de transactions valides, au format attendu par /predict-batch."""
    rng = np.random.default_rng(0)
    n = 15
    data = {"Time": rng.uniform(0, 172792, n), "Amount": rng.exponential(60, n)}
    for i in range(1, 29):
        data[f"V{i}"] = rng.normal(0, 1, n)
    return pd.DataFrame(data)