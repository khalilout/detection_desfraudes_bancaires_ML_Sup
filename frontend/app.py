# import os
# from pathlib import Path

# import numpy as np
# import pandas as pd
# import plotly.graph_objects as go
# import requests
# import streamlit as st

# st.set_page_config(
#     page_title="FraudGuard — Détection de fraude",
#     page_icon="🛡️",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )


# def _resolve_api_url() -> str:
#     secrets_paths = [
#         Path(".streamlit/secrets.toml"),
#         Path.home() / ".streamlit" / "secrets.toml",
#     ]
#     if any(p.exists() for p in secrets_paths):
#         try:
#             return st.secrets["API_URL"]
#         except Exception:
#             pass
#     return os.environ.get("API_URL", "https://detection-desfraudes-bancaires-ml.onrender.com")


# API_URL = _resolve_api_url()

# st.markdown("""
# <style>
#     .main { background-color: #0e1117; }
#     .hero {
#         background: linear-gradient(135deg, #1a1f2e 0%, #0e1117 100%);
#         border: 1px solid #2d3348;
#         border-radius: 16px;
#         padding: 2.2rem 2.5rem;
#         margin-bottom: 1.5rem;
#     }
#     .hero h1 { font-size: 2.1rem; margin-bottom: 0.3rem; }
#     .hero p { color: #9aa4b8; font-size: 1.02rem; margin: 0; }
#     .metric-card {
#         background: #161b26;
#         border: 1px solid #2d3348;
#         border-radius: 12px;
#         padding: 1rem 1.2rem;
#         text-align: center;
#     }
#     .metric-card .label { color: #9aa4b8; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; }
#     .metric-card .value { font-size: 1.5rem; font-weight: 700; margin-top: 0.2rem; }
#     .badge-safe { background: #113a2a; color: #4ade80; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; display: inline-block; }
#     .badge-danger { background: #3a1414; color: #f87171; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; display: inline-block; }
#     section[data-testid="stSidebar"] { background-color: #131722; }
# </style>
# """, unsafe_allow_html=True)


# st.markdown("""
# <div class="hero">
#     <h1>🛡️ FraudGuard</h1>
#     <p>Détection de fraude bancaire en temps réel — modèle XGBoost entraîné sur 284 807 transactions réelles (dataset Kaggle Credit Card Fraud, ULB).</p>
# </div>
# """, unsafe_allow_html=True)


# with st.sidebar:
#     st.markdown("### ⚙️ À propos du modèle")
#     info_response = requests.get(f"{API_URL}/model-info")
#     if info_response.status_code == 200:
#         info = info_response.json()
#         st.markdown(f"**Algorithme** : {info['model_type']}")
#         st.markdown(f"**Seuil de décision** : {info['decision_threshold']:.4f}")
#         st.markdown(f"**Variables utilisées** : {info['n_features']}")
#         st.success("API connectée ✅")
#     else:
#         st.error("⚠️ API injoignable")
#         st.caption(f"Tentative sur : {API_URL}")
#         st.stop()

#     st.divider()
#     st.markdown("### 📊 Le dataset en bref")
#     st.markdown("""
#     - **284 807** transactions
#     - **492** fraudes (0,17%)
#     - Variables `V1`-`V28` anonymisées par PCA
#     - `Time` et `Amount` en clair
#     """)
#     st.divider()
#     st.caption("Stack : FastAPI · XGBoost · scikit-learn · Streamlit")

# tab1, tab2 = st.tabs(["🔍  Analyser une transaction", "📁  Analyser un lot (CSV)"])


# with tab1:
#     st.markdown("#### Simuler une transaction")
#     st.caption("Les variables `V1` à `V28` sont anonymisées (PCA) : impossible de les saisir « à la main » de façon réaliste. Utilisez les boutons de démonstration ci-dessous, ou ajustez manuellement dans le panneau avancé.")

#     demo_col1, demo_col2, demo_col3 = st.columns(3)

#     def _random_profile(fraud_like: bool) -> dict:
#         rng = np.random.default_rng()
#         if fraud_like:
            
#             v = {f"V{i}": float(rng.normal(0, 3)) for i in range(1, 29)}
#             amount = float(rng.uniform(1, 5))
#         else:
#             v = {f"V{i}": float(rng.normal(0, 1)) for i in range(1, 29)}
#             amount = float(rng.exponential(60))
#         return {"Time": float(rng.uniform(0, 172792)), "Amount": round(amount, 2), **v}

#     if "transaction_payload" not in st.session_state:
#         st.session_state.transaction_payload = _random_profile(fraud_like=False)

#     if demo_col1.button("🎲 Transaction aléatoire", use_container_width=True):
#         st.session_state.transaction_payload = _random_profile(fraud_like=False)
#     if demo_col2.button("🚩 Profil suspect (démo)", use_container_width=True):
#         st.session_state.transaction_payload = _random_profile(fraud_like=True)
#     if demo_col3.button("🧹 Réinitialiser (zéros)", use_container_width=True):
#         st.session_state.transaction_payload = {"Time": 0.0, "Amount": 0.0, **{f"V{i}": 0.0 for i in range(1, 29)}}

#     payload = st.session_state.transaction_payload

#     c1, c2 = st.columns(2)
#     payload["Time"] = c1.number_input("Time (secondes écoulées)", value=float(payload["Time"]), step=1.0)
#     payload["Amount"] = c2.number_input("Amount (€)", value=float(payload["Amount"]), min_value=0.0, step=1.0)

#     with st.expander("🔧 Ajuster les composantes V1 à V28 (panneau avancé)"):
#         cols = st.columns(7)
#         for i in range(1, 29):
#             with cols[(i - 1) % 7]:
#                 payload[f"V{i}"] = st.number_input(f"V{i}", value=float(payload[f"V{i}"]), key=f"v_{i}")

#     st.write("")
#     if st.button("🔎 Analyser cette transaction", type="primary", use_container_width=True):
#         with st.spinner("Analyse en cours..."):
#             response = requests.post(f"{API_URL}/predict", json=payload)

#         if response.status_code == 200:
#             result = response.json()
#             proba_pct = result["fraud_probability"] * 100
#             threshold_pct = result["decision_threshold"] * 100

#             res_col1, res_col2 = st.columns([1, 1.3])

#             with res_col1:
#                 if result["is_fraud"]:
#                     st.markdown('<span class="badge-danger">⚠️ FRAUDE PROBABLE</span>', unsafe_allow_html=True)
#                 else:
#                     st.markdown('<span class="badge-safe">✅ TRANSACTION NORMALE</span>', unsafe_allow_html=True)
#                 st.metric("Probabilité de fraude", f"{proba_pct:.2f}%")
#                 st.caption(f"Seuil de décision du modèle : {threshold_pct:.2f}%")

#             with res_col2:
#                 fig = go.Figure(go.Indicator(
#                     mode="gauge+number",
#                     value=proba_pct,
#                     number={"suffix": "%"},
#                     gauge={
#                         "axis": {"range": [0, 100]},
#                         "bar": {"color": "#f87171" if result["is_fraud"] else "#4ade80"},
#                         "steps": [
#                             {"range": [0, threshold_pct], "color": "#113a2a"},
#                             {"range": [threshold_pct, 100], "color": "#3a1414"},
#                         ],
#                         "threshold": {
#                             "line": {"color": "white", "width": 3},
#                             "thickness": 0.9,
#                             "value": threshold_pct,
#                         },
#                     },
#                 ))
#                 fig.update_layout(height=220, margin=dict(l=20, r=20, t=20, b=20),
#                                    paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"})
#                 st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.error(f"Erreur : {response.text}")


# with tab2:
#     st.markdown("#### Analyser un lot de transactions")
#     st.caption("Uploadez un CSV contenant les colonnes `Time`, `V1`...`V28`, `Amount` (sans la colonne `Class`).")

#     uploaded_file = st.file_uploader("Fichier CSV", type=["csv"], label_visibility="collapsed")

#     if uploaded_file is not None:
#         if st.button("🔎 Analyser le lot", type="primary"):
#             with st.spinner("Analyse en cours..."):
#                 files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
#                 response = requests.post(f"{API_URL}/predict-batch", files=files)

#             if response.status_code == 200:
#                 result = response.json()

#                 m1, m2, m3 = st.columns(3)
#                 m1.markdown(f'<div class="metric-card"><div class="label">Transactions</div><div class="value">{result["n_transactions"]}</div></div>', unsafe_allow_html=True)
#                 m2.markdown(f'<div class="metric-card"><div class="label">Fraudes détectées</div><div class="value" style="color:#f87171">{result["n_predicted_fraud"]}</div></div>', unsafe_allow_html=True)
#                 fraud_rate = result["n_predicted_fraud"] / result["n_transactions"] * 100 if result["n_transactions"] else 0
#                 m3.markdown(f'<div class="metric-card"><div class="label">Taux de fraude</div><div class="value">{fraud_rate:.2f}%</div></div>', unsafe_allow_html=True)

#                 st.write("")
#                 preview_df = pd.read_csv(uploaded_file)
#                 preview_df["fraud_probability"] = [p["fraud_probability"] for p in result["predictions"]]
#                 preview_df["is_fraud"] = [p["is_fraud"] for p in result["predictions"]]
#                 preview_df = preview_df.sort_values("fraud_probability", ascending=False)

#                 st.markdown("**Distribution des probabilités de fraude**")
#                 st.bar_chart(preview_df["fraud_probability"].reset_index(drop=True))

#                 st.markdown("**Résultats détaillés** (triés par risque décroissant)")

#                 def _highlight_fraud(row):
#                     return ["background-color: #3a1414" if row["is_fraud"] else "" for _ in row]

#                 st.dataframe(
#                     preview_df.style.apply(_highlight_fraud, axis=1),
#                     use_container_width=True,
#                     height=400,
#                 )

#                 csv_out = preview_df.to_csv(index=False).encode("utf-8")
#                 st.download_button(
#                     "⬇️ Télécharger les résultats", data=csv_out,
#                     file_name="resultats_fraude.csv", mime="text/csv",
#                     use_container_width=True,
#                 )
#             else:
#                 st.error(f"Erreur : {response.json().get('detail', response.text)}")

# st.divider()
# st.caption("FraudGuard · Projet portfolio · Modèle non destiné à un usage en production réelle sans validation métier complémentaire.")









import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    IsolationForest,
    BaggingClassifier
)
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import warnings

# Ignorer les avertissements pour une meilleure lisibilité dans Streamlit
warnings.filterwarnings('ignore')

# --- Configuration de la page Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="Détection de Fraude Bancaire  fraudbusters 🛡️",
    initial_sidebar_state="expanded"
)

# --- Constantes du Projet ---
FILE_PATH = 'data_project.csv'
TARGET = 'FlagImpaye'
ID_COLUMNS = ['ZIBZIN', 'IDAvisAutorisationCheque', 'Heure']
DATE_COLUMN = 'DateTransaction'
SAMPLE_FRACTION = 0.30  # Échantillonnage à 30% des données

# --- 0. Fonctions de Chargement et de Préparation ---

@st.cache_data(show_spinner="⏳ Chargement, échantillonnage et préparation des données...")
def load_and_sample_data(file_path, sample_frac):
    """Charge le CSV, applique le formatage, et échantillonne."""
    try:
        df = pd.read_csv(
            file_path, sep=';', decimal=',', dayfirst=True, parse_dates=[DATE_COLUMN]
        )
    except Exception:
        df = pd.read_csv(file_path, sep=';', decimal=',', dayfirst=True)
        df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors='coerce')

    df[TARGET] = df[TARGET].astype(int)

    # Échantillonnage aléatoire (30% des données)
    df_sampled = df.sample(frac=sample_frac, random_state=42).sort_values(by=DATE_COLUMN).reset_index(drop=True)
    
    # Séparation temporelle (80% train, 20% test)
    split_index = int(0.8 * len(df_sampled))
    train_df = df_sampled.iloc[:split_index].copy()
    test_df = df_sampled.iloc[split_index:].copy()

    X_train_base = train_df.drop([TARGET] + ID_COLUMNS + [DATE_COLUMN], axis=1)
    y_train_base = train_df[TARGET]
    X_test_base = test_df.drop([TARGET] + ID_COLUMNS + [DATE_COLUMN], axis=1)
    y_test_base = test_df[TARGET]
    
    return X_train_base, y_train_base, X_test_base, y_test_base, df_sampled

# --- 1. Fonction de l'ensemble de la Pipeline ML ---

@st.cache_data(show_spinner="🚀 Exécution complète de la Pipeline ML (I1, I2, Bagging)...")
def execute_ml_pipeline(X_train_base, y_train_base, X_test_base, y_test_base):
    """Exécute les étapes de la pipeline ML."""
    
    numeric_features = X_train_base.columns.tolist()
    
    # 3. Prétraitement
    preprocessor = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    X_train_scaled = pd.DataFrame(preprocessor.fit_transform(X_train_base), columns=numeric_features, index=X_train_base.index)
    X_test_scaled = pd.DataFrame(preprocessor.transform(X_test_base), columns=numeric_features, index=X_test_base.index)
    
    # PARTIE 4 : Feature Engineering (IsolationForest)
    new_feature_name = 'Isolation_Anomaly_Score'
    X_train_no_fraud = X_train_scaled[y_train_base == 0]
    iforest = IsolationForest(contamination='auto', random_state=42, n_jobs=-1)
    iforest.fit(X_train_no_fraud)

    X_train_i2 = X_train_scaled.copy()
    X_test_i2 = X_test_scaled.copy()
    X_train_i2[new_feature_name] = -iforest.decision_function(X_train_i2)
    X_test_i2[new_feature_name] = -iforest.decision_function(X_test_i2)

    # 5. Gestion du déséquilibre (SMOTE)
    X_train_i1 = X_train_scaled 
    X_test_i1 = X_test_scaled.drop(new_feature_name, axis=1) 
    
    smote = SMOTE(random_state=42)
    X_train_smote_i1, y_train_smote_i1 = smote.fit_resample(X_train_i1, y_train_base)
    X_train_smote_i2, y_train_smote_i2 = smote.fit_resample(X_train_i2, y_train_base)
    
    
    # PARTIE 2 : Modélisation et Évaluation (I1 et I2)
    MODELS = {
        'LogisticRegression': LogisticRegression(solver='liblinear', random_state=42),
        'RandomForest': RandomForestClassifier(random_state=42, n_estimators=100, max_depth=10, n_jobs=-1),
        'GradientBoosting': GradientBoostingClassifier(random_state=42, n_estimators=100, max_depth=5),
        'CostSensitive_LogReg': LogisticRegression(solver='liblinear', random_state=42, class_weight='balanced'),
    }
    
    results = []
    param_grid = {'max_depth': [5, 10], 'n_estimators': [50, 100]}
    
    # ITÉRATION 1
    for name, model in MODELS.items():
        model.fit(X_train_smote_i1, y_train_smote_i1)
        f1 = f1_score(y_test_base, model.predict(X_test_i1))
        results.append({'Modèle': name, 'Itération': 'I1 (Baseline)', 'F1-Score': f1, 'ModelObject': model, 'X_test': X_test_i1})
        
    grid_search_i1 = GridSearchCV(RandomForestClassifier(random_state=42, n_jobs=-1), param_grid, scoring='f1', cv=3, n_jobs=-1)
    grid_search_i1.fit(X_train_smote_i1, y_train_smote_i1)
    f1_grid_i1 = f1_score(y_test_base, grid_search_i1.best_estimator_.predict(X_test_i1))
    results.append({'Modèle': 'GridSearch_RF', 'Itération': 'I1 (Baseline)', 'F1-Score': f1_grid_i1, 'ModelObject': grid_search_i1.best_estimator_, 'X_test': X_test_i1})


    # ITÉRATION 2
    for name, model in MODELS.items():
        model_clone = model.__class__(**model.get_params())
        model_clone.fit(X_train_smote_i2, y_train_smote_i2)
        f1 = f1_score(y_test_base, model_clone.predict(X_test_i2))
        results.append({'Modèle': name, 'Itération': 'I2 (+IF Score)', 'F1-Score': f1, 'ModelObject': model_clone, 'X_test': X_test_i2})

    grid_search_i2 = GridSearchCV(RandomForestClassifier(random_state=42, n_jobs=-1), param_grid, scoring='f1', cv=3, n_jobs=-1)
    grid_search_i2.fit(X_train_smote_i2, y_train_smote_i2)
    f1_grid_i2 = f1_score(y_test_base, grid_search_i2.best_estimator_.predict(X_test_i2))
    results.append({'Modèle': 'GridSearch_RF', 'Itération': 'I2 (+IF Score)', 'F1-Score': f1_grid_i2, 'ModelObject': grid_search_i2.best_estimator_, 'X_test': X_test_i2})
    
    results_df = pd.DataFrame(results)

    # PARTIE 3 : Post-traitement (Bagging)
    best_i2 = results_df[results_df['Itération'] == 'I2 (+IF Score)'].sort_values(by='F1-Score', ascending=False).iloc[0]
    base_estimator_i2 = best_i2['ModelObject']
    bagging_model = BaggingClassifier(estimator=base_estimator_i2, n_estimators=10, random_state=42, n_jobs=-1)

    bagging_model.fit(X_train_smote_i2, y_train_smote_i2)
    f1_bagging = f1_score(y_test_base, bagging_model.predict(X_test_i2))

    results.append({
        'Modèle': 'Bagging_Final', 'Itération': f"Post-traitement ({best_i2['Modèle']})",
        'F1-Score': f1_bagging, 'ModelObject': bagging_model, 'X_test': X_test_i2
    })
    
    final_results_df = pd.DataFrame(results)
    
    return final_results_df, y_test_base

# ==============================================================================
# STRUCTURE DE L'APPLICATION STREAMLIT
# ==============================================================================

st.title("🛡️ Projet Détection de Fraude Bancaire par Machine Learning")
st.markdown("---")

# --- 1. CONFIGURATION et Chargement des Données ---
st.header("1. Configuration du Projet et Chargement des Données")
col1, col2, col3 = st.columns(3)

try:
    X_train_base, y_train_base, X_test_base, y_test_base, df_sampled = load_and_sample_data(FILE_PATH, SAMPLE_FRACTION)
    
    total_fraudes = y_train_base.sum() + y_test_base.sum()
    
    with col1:
        st.metric(label="Taille Totale de l'Échantillon", value=f"{len(df_sampled):,} lignes")
    with col2:
        st.metric(label="Ratio d'Échantillonnage", value=f"{SAMPLE_FRACTION*100:.0f}%")
    with col3:
        st.metric(label="Incidence de la Fraude", value=f"{total_fraudes / len(df_sampled) * 100:.3f}%", help="Classe positive (FlagImpaye=1) dans l'échantillon.")
    
    st.success("✅ **Chargement réussi.** Pipeline ML prête à être exécutée.")
    
    # Exécuter la pipeline complète
    results_df, y_test_base_final = execute_ml_pipeline(X_train_base, y_train_base, X_test_base, y_test_base)
    
except FileNotFoundError:
    st.error(f"❌ Erreur: Le fichier '{FILE_PATH}' n'a pas été trouvé. Veuillez le placer dans le même dossier.")
    st.stop()
except Exception as e:
    st.error(f"❌ Une erreur est survenue lors du chargement/traitement des données. Erreur: {e}")
    st.stop()


# --- 2. Résultats de Modélisation (Tableau Récapitulatif) ---

st.header("2. Résultats et Comparaison des Modèles")
st.markdown("### Tableau Récapitulatif des F1-Scores")

# Calcul des améliorations par rapport à la baseline (I1)
comparison_df = results_df.drop(columns=['ModelObject', 'X_test']).copy()
comparison_df['F1-Score sur Test'] = comparison_df['F1-Score'].round(4)
comparison_df = comparison_df.sort_values(by=['Itération', 'F1-Score'], ascending=[False, False]).reset_index(drop=True)

# Calculer Delta I2 vs I1 (Baseline)
baseline_scores = comparison_df[comparison_df['Itération'] == 'I1 (Baseline)'].set_index('Modèle')['F1-Score']
def calculate_improvement(row):
    if row['Itération'] == 'I2 (+IF Score)':
        baseline_score = baseline_scores.get(row['Modèle'])
        if baseline_score:
            delta = row['F1-Score'] - baseline_score
            perc = delta / baseline_score
            return f"{delta:.4f} ({perc*100:+.2f}%)"
    return 'N/A'

comparison_df['Amélioration vs I1 (Baseline)'] = comparison_df.apply(calculate_improvement, axis=1)

# Formatage final du tableau
comparison_df.drop(columns=['F1-Score'], inplace=True)
comparison_df.rename(columns={'Modèle': 'Modèle de Base'}, inplace=True)

st.dataframe(comparison_df.style.background_gradient(cmap=sns.light_palette("darkred", as_cmap=True), subset=['F1-Score sur Test']), use_container_width=True)

st.caption("Le score d'anomalie 'IF Score' a été ajouté dans l'Itération 2.")

# --- Graphique de Comparaison ---

st.subheader("Visualisation de l'Impact de l'Itération 2")
df_plot = results_df.drop(columns=['ModelObject', 'X_test'])
df_plot['Modèle Complet'] = df_plot['Modèle'] + " (" + df_plot['Itération'].str.split(' ').str[0] + ")"
df_plot['F1-Score'] = df_plot['F1-Score'].round(4)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=df_plot, x='Modèle', y='F1-Score', hue='Itération', palette=['#1f77b4', '#ff7f0e'], ax=ax)
ax.set_title("Comparaison des F1-Scores par Modèle et Itération", fontsize=16)
ax.set_ylabel("F1-Score", fontsize=14)
ax.set_xlabel("Algorithme", fontsize=14)
plt.xticks(rotation=15)
st.pyplot(fig)


# --- 3. Synthèse et Modèle Final ---
st.markdown("---")
st.header("3. Modèle Final et Analyse Détaillée")

final_model_row = results_df.sort_values(by='F1-Score', ascending=False).iloc[0]
best_model_name = final_model_row['Modèle']
best_f1_score = final_model_row['F1-Score']
final_model_object = final_model_row['ModelObject']
X_test_final = final_model_row['X_test']

st.markdown(f"""
    Le **Modèle Final Retenu** est le **:trophy: {best_model_name}** (issu de l'itération **{final_model_row['Itération']}**).
""")

col_metric, col_report, col_matrix = st.columns([1, 1.5, 2])

with col_metric:
    st.subheader("Performance Clé")
    st.metric(label="F1-Score Maximal Atteint", value=f"{best_f1_score:.4f}", delta=f"{best_f1_score-df_plot['F1-Score'].max():.4f}" if best_model_name == 'Bagging_Final' else None, delta_color="normal")
    
    st.info("Le F1-Score est la métrique la plus pertinente pour le déséquilibre de classes.")

with col_report:
    st.subheader("Rapport de Classification")
    y_pred_final = final_model_object.predict(X_test_final)
    report = classification_report(y_test_base_final, y_pred_final, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    st.dataframe(report_df[['precision', 'recall', 'f1-score', 'support']].style.format({'precision': "{:.3f}", 'recall': "{:.3f}", 'f1-score': "{:.3f}", 'support': "{:.0f}"}), use_container_width=True)

with col_matrix:
    st.subheader("Matrice de Confusion (Modèle Final)")
    cm = confusion_matrix(y_test_base_final, y_pred_final)
    fig_cm, ax_cm = plt.subplots(figsize=(5, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Reds', cbar=False,
                xticklabels=['Non-Fraude (0)', 'Fraude (1)'],
                yticklabels=['Non-Fraude (0)', 'Fraude (1)'], ax=ax_cm)
    ax_cm.set_xlabel('Prédiction')
    ax_cm.set_ylabel('Vérité Terrain')
    st.pyplot(fig_cm)
    
    st.markdown("""
        ⚠️ Les **Faux Négatifs (FN)** (fraudes manquées) représentent le coût le plus élevé. Une augmentation du **Rappel (Recall)** est souhaitable.
    """)


# --- 4. Conclusion et Perspectives ---
st.markdown("---")
st.header("4. Conclusion et Pistes d'Amélioration")

st.markdown("""
### 💡 Conclusion
Le travail sur l'échantillon de 30% a permis d'établir une pipeline robuste. L'approche d'ensemble (Gradient Boosting ou Random Forest) s'est avérée la plus performante. L'intégration d'un signal d'anomalie non supervisé (`Isolation_Anomaly_Score`) a validé l'idée que le *Feature Engineering* est essentiel pour cette problématique.

### 🔭 Perspectives d'Amélioration
Étant donné la difficulté intrinsèque de la détection de fraude sur des données réelles, les pistes suivantes sont suggérées pour affiner la performance :
1.  **Optimisation Coût-Sensible (XGBoost/LightGBM)** : Utiliser des modèles de *boosting* avancés avec des **fonctions de coût personnalisées** pour pénaliser les Faux Négatifs bien plus lourdement que les Faux Positifs.
2.  **Autoencodeurs** : Explorer l'utilisation des **Autoencodeurs Variationnels (VAE)** pour générer un score d'anomalie plus sophistiqué que l'Isolation Forest, en exploitant la puissance du Deep Learning pour modéliser le comportement normal (Non-Fraude).
3.  **Suréchantillonnage Ciblée** : Remplacer le SMOTE par **ADASYN**, qui génère des échantillons synthétiques préférentiellement pour les instances minoritaires les plus difficiles à classer, permettant de mieux définir la frontière de décision.
""")