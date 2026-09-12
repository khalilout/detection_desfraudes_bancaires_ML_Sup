import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="FraudGuard — Détection de fraude",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _resolve_api_url() -> str:
    secrets_paths = [
        Path(".streamlit/secrets.toml"),
        Path.home() / ".streamlit" / "secrets.toml",
    ]
    if any(p.exists() for p in secrets_paths):
        try:
            return st.secrets["API_URL"]
        except Exception:
            pass
    return os.environ.get("API_URL", "https://detection-desfraudes-bancaires-ml.onrender.com")


API_URL = _resolve_api_url()

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .hero {
        background: linear-gradient(135deg, #1a1f2e 0%, #0e1117 100%);
        border: 1px solid #2d3348;
        border-radius: 16px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 1.5rem;
    }
    .hero h1 { font-size: 2.1rem; margin-bottom: 0.3rem; }
    .hero p { color: #9aa4b8; font-size: 1.02rem; margin: 0; }
    .metric-card {
        background: #161b26;
        border: 1px solid #2d3348;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-card .label { color: #9aa4b8; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card .value { font-size: 1.5rem; font-weight: 700; margin-top: 0.2rem; }
    .badge-safe { background: #113a2a; color: #4ade80; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; display: inline-block; }
    .badge-danger { background: #3a1414; color: #f87171; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; display: inline-block; }
    section[data-testid="stSidebar"] { background-color: #131722; }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>🛡️ FraudGuard</h1>
    <p>Détection de fraude bancaire en temps réel — modèle XGBoost entraîné sur 284 807 transactions réelles (dataset Kaggle Credit Card Fraud, ULB).</p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("### ⚙️ À propos du modèle")
    info_response = requests.get(f"{API_URL}/model-info")
    if info_response.status_code == 200:
        info = info_response.json()
        st.markdown(f"**Algorithme** : {info['model_type']}")
        st.markdown(f"**Seuil de décision** : {info['decision_threshold']:.4f}")
        st.markdown(f"**Variables utilisées** : {info['n_features']}")
        st.success("API connectée ✅")
    else:
        st.error("⚠️ API injoignable")
        st.caption(f"Tentative sur : {API_URL}")
        st.stop()

    st.divider()
    st.markdown("### 📊 Le dataset en bref")
    st.markdown("""
    - **284 807** transactions
    - **492** fraudes (0,17%)
    - Variables `V1`-`V28` anonymisées par PCA
    - `Time` et `Amount` en clair
    """)
    st.divider()
    st.caption("Stack : FastAPI · XGBoost · scikit-learn · Streamlit")

tab1, tab2 = st.tabs(["🔍  Analyser une transaction", "📁  Analyser un lot (CSV)"])


with tab1:
    st.markdown("#### Simuler une transaction")
    st.caption("Les variables `V1` à `V28` sont anonymisées (PCA) : impossible de les saisir « à la main » de façon réaliste. Utilisez les boutons de démonstration ci-dessous, ou ajustez manuellement dans le panneau avancé.")

    demo_col1, demo_col2, demo_col3 = st.columns(3)

    def _random_profile(fraud_like: bool) -> dict:
        rng = np.random.default_rng()
        if fraud_like:
            
            v = {f"V{i}": float(rng.normal(0, 3)) for i in range(1, 29)}
            amount = float(rng.uniform(1, 5))
        else:
            v = {f"V{i}": float(rng.normal(0, 1)) for i in range(1, 29)}
            amount = float(rng.exponential(60))
        return {"Time": float(rng.uniform(0, 172792)), "Amount": round(amount, 2), **v}

    if "transaction_payload" not in st.session_state:
        st.session_state.transaction_payload = _random_profile(fraud_like=False)

    if demo_col1.button("🎲 Transaction aléatoire", use_container_width=True):
        st.session_state.transaction_payload = _random_profile(fraud_like=False)
    if demo_col2.button("🚩 Profil suspect (démo)", use_container_width=True):
        st.session_state.transaction_payload = _random_profile(fraud_like=True)
    if demo_col3.button("🧹 Réinitialiser (zéros)", use_container_width=True):
        st.session_state.transaction_payload = {"Time": 0.0, "Amount": 0.0, **{f"V{i}": 0.0 for i in range(1, 29)}}

    payload = st.session_state.transaction_payload

    c1, c2 = st.columns(2)
    payload["Time"] = c1.number_input("Time (secondes écoulées)", value=float(payload["Time"]), step=1.0)
    payload["Amount"] = c2.number_input("Amount (€)", value=float(payload["Amount"]), min_value=0.0, step=1.0)

    with st.expander("🔧 Ajuster les composantes V1 à V28 (panneau avancé)"):
        cols = st.columns(7)
        for i in range(1, 29):
            with cols[(i - 1) % 7]:
                payload[f"V{i}"] = st.number_input(f"V{i}", value=float(payload[f"V{i}"]), key=f"v_{i}")

    st.write("")
    if st.button("🔎 Analyser cette transaction", type="primary", use_container_width=True):
        with st.spinner("Analyse en cours..."):
            response = requests.post(f"{API_URL}/predict", json=payload)

        if response.status_code == 200:
            result = response.json()
            proba_pct = result["fraud_probability"] * 100
            threshold_pct = result["decision_threshold"] * 100

            res_col1, res_col2 = st.columns([1, 1.3])

            with res_col1:
                if result["is_fraud"]:
                    st.markdown('<span class="badge-danger">⚠️ FRAUDE PROBABLE</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-safe">✅ TRANSACTION NORMALE</span>', unsafe_allow_html=True)
                st.metric("Probabilité de fraude", f"{proba_pct:.2f}%")
                st.caption(f"Seuil de décision du modèle : {threshold_pct:.2f}%")

            with res_col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=proba_pct,
                    number={"suffix": "%"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#f87171" if result["is_fraud"] else "#4ade80"},
                        "steps": [
                            {"range": [0, threshold_pct], "color": "#113a2a"},
                            {"range": [threshold_pct, 100], "color": "#3a1414"},
                        ],
                        "threshold": {
                            "line": {"color": "white", "width": 3},
                            "thickness": 0.9,
                            "value": threshold_pct,
                        },
                    },
                ))
                fig.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=20),
                                   paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"})
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Erreur : {response.text}")


with tab2:
    st.markdown("#### Analyser un lot de transactions")
    st.caption("Uploadez un CSV contenant les colonnes `Time`, `V1`...`V28`, `Amount` (sans la colonne `Class`).")

    uploaded_file = st.file_uploader("Fichier CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        if st.button("🔎 Analyser le lot", type="primary"):
            with st.spinner("Analyse en cours..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(f"{API_URL}/predict-batch", files=files)

            if response.status_code == 200:
                result = response.json()

                m1, m2, m3 = st.columns(3)
                m1.markdown(f'<div class="metric-card"><div class="label">Transactions</div><div class="value">{result["n_transactions"]}</div></div>', unsafe_allow_html=True)
                m2.markdown(f'<div class="metric-card"><div class="label">Fraudes détectées</div><div class="value" style="color:#f87171">{result["n_predicted_fraud"]}</div></div>', unsafe_allow_html=True)
                fraud_rate = result["n_predicted_fraud"] / result["n_transactions"] * 100 if result["n_transactions"] else 0
                m3.markdown(f'<div class="metric-card"><div class="label">Taux de fraude</div><div class="value">{fraud_rate:.2f}%</div></div>', unsafe_allow_html=True)

                st.write("")
                preview_df = pd.read_csv(uploaded_file)
                preview_df["fraud_probability"] = [p["fraud_probability"] for p in result["predictions"]]
                preview_df["is_fraud"] = [p["is_fraud"] for p in result["predictions"]]
                preview_df = preview_df.sort_values("fraud_probability", ascending=False)

                st.markdown("**Distribution des probabilités de fraude**")
                st.bar_chart(preview_df["fraud_probability"].reset_index(drop=True))

                st.markdown("**Résultats détaillés** (triés par risque décroissant)")

                def _highlight_fraud(row):
                    return ["background-color: #3a1414" if row["is_fraud"] else "" for _ in row]

                st.dataframe(
                    preview_df.style.apply(_highlight_fraud, axis=1),
                    use_container_width=True,
                    height=400,
                )

                csv_out = preview_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Télécharger les résultats", data=csv_out,
                    file_name="resultats_fraude.csv", mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.error(f"Erreur : {response.json().get('detail', response.text)}")

st.divider()
st.caption("FraudGuard · Projet portfolio · Modèle non destiné à un usage en production réelle sans validation métier complémentaire.")