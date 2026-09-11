import numpy as np
import pandas as pd
import pytest

from backend.app.inference import FraudDetector, detector


def test_detector_loads_successfully():
    assert detector.model is not None
    assert detector.scaler_amount is not None
    assert detector.scaler_time is not None
    assert isinstance(detector.feature_order, list)
    assert len(detector.feature_order) == 30  # Time + V1-V28 + Amount


def test_feature_order_matches_expected_columns():
    expected = {"Time", "Amount"} | {f"V{i}" for i in range(1, 29)}
    assert set(detector.feature_order) == expected


def test_predict_proba_returns_values_between_0_and_1(sample_batch_df):
    probabilities = detector.predict_proba(sample_batch_df)
    assert len(probabilities) == len(sample_batch_df)
    assert all(0.0 <= p <= 1.0 for p in probabilities)


def test_predict_returns_expected_keys(sample_batch_df):
    results = detector.predict(sample_batch_df)
    assert len(results) == len(sample_batch_df)
    for r in results:
        assert set(r.keys()) == {"is_fraud", "fraud_probability", "decision_threshold"}
        assert isinstance(r["is_fraud"], bool)
        assert r["decision_threshold"] == detector.decision_threshold


def test_predict_is_fraud_consistent_with_threshold(sample_batch_df):
    """La décision is_fraud doit toujours correspondre à probabilité >= seuil."""
    results = detector.predict(sample_batch_df)
    for r in results:
        expected = r["fraud_probability"] >= r["decision_threshold"]
        assert r["is_fraud"] == expected


def test_prepare_reorders_columns_regardless_of_input_order(sample_batch_df):
    """Le detector doit fonctionner même si les colonnes du CSV ne sont pas dans l'ordre attendu."""
    shuffled = sample_batch_df[sample_batch_df.columns[::-1]]
    result_ordered = detector.predict(sample_batch_df)
    result_shuffled = detector.predict(shuffled)
    for a, b in zip(result_ordered, result_shuffled):
        assert abs(a["fraud_probability"] - b["fraud_probability"]) < 1e-9


def test_scaling_is_applied_not_raw_values(sample_batch_df):
    """Vérifie que le scaler transforme bien Amount/Time (pas juste un passage direct)."""
    prepared = detector._prepare(sample_batch_df)
    assert not np.allclose(prepared["Amount"].values, sample_batch_df["Amount"].values)
    assert not np.allclose(prepared["Time"].values, sample_batch_df["Time"].values)