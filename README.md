# 🛡️ FraudGuard — Détection de fraude par carte bancaire

Application complète de détection de fraude bancaire : exploration & modélisation en notebook, API de scoring temps réel (FastAPI), dashboard interactif (Streamlit), le tout conteneurisé et testé.

**Dataset** : [Credit Card Fraud Detection (ULB)](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) — 284 807 transactions bancaires européennes, 492 fraudes (0,17%).

## Sommaire

- [Architecture](#architecture)
- [Résultats du modèle](#résultats-du-modèle)
- [Installation locale](#installation-locale)
- [Lancer avec Docker](#lancer-avec-docker)
- [Tests](#tests)
- [Structure du projet](#structure-du-projet)

## Architecture

```
┌─────────────────┐      HTTP       ┌──────────────────┐
│  Streamlit UI    │ ──────────────> │   FastAPI         │
│  (frontend/)      │ <────────────── │   (backend/app/)   │
└─────────────────┘                  └──────────────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │  Modèle XGBoost   │
                                     │  (models/*.joblib)│
                                     └──────────────────┘
```

Le modèle est entraîné une fois dans le notebook (`notebooks/`), sauvegardé sur disque, puis chargé par l'API au démarrage — aucune dépendance à Jupyter en production.

## Résultats du modèle

Comparaison de 3 modèles sur un split test stratifié (20% des données, jamais vu à l'entraînement) :

| Modèle | Precision (fraude) | Recall (fraude) | F1 | PR-AUC |
|---|---|---|---|---|
| Logistic Regression (`class_weight=balanced`) | 0,061 | 0,918 | 0,114 | 0,716 |
| Random Forest (`class_weight=balanced`) | 0,842 | 0,816 | 0,829 | 0,829 |
| **XGBoost (`scale_pos_weight`)** | **0,882** | 0,837 | 0,859 | **0,879** |

**XGBoost retenu**, avec un seuil de décision optimisé (0,9238 au lieu de 0,5 par défaut) qui améliore encore le compromis :

| | Seuil 0,5 (défaut) | Seuil optimisé (0,9238) |
|---|---|---|
| Precision | 0,882 | **0,942** |
| Recall | 0,837 | 0,827 |
| F1 | 0,859 | **0,880** |

**Validation croisée** (5 folds stratifiés) : PR-AUC moyen de 0,855 (± 0,018) — performance stable, pas un artefact du split initial.

**SMOTE testé et écarté** : le sur-échantillonnage synthétique donne un PR-AUC légèrement inférieur (0,862) à la simple pondération de classe — sur ce dataset, `scale_pos_weight` est suffisant et plus simple.

⚠️ **L'accuracy n'est jamais utilisée comme métrique de référence** dans ce projet : avec 99,83% de transactions normales, un modèle qui prédit toujours "normal" atteindrait déjà 99,83% d'accuracy sans détecter la moindre fraude. Toutes les décisions s'appuient sur precision/recall/F1/PR-AUC.

## Installation locale

```bash
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate

pip install -r requirements-backend.txt
pip install -r requirements-frontend.txt
```

### 1. Entraîner le modèle (si `models/` est vide)

Téléchargez `creditcard.csv` depuis [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud), placez-le dans `data/`, puis exécutez `notebooks/01_exploration_et_modelisation.ipynb` de bout en bout. Ça génère `models/fraud_model.joblib`, `scaler_amount.joblib`, `scaler_time.joblib` et `model_config.json`.

### 2. Lancer l'API

```bash
uvicorn backend.app.main:app --reload --port 8000
```
Documentation interactive : http://localhost:8000/docs

### 3. Lancer le dashboard

Dans un second terminal :
```bash
streamlit run frontend/app.py
```
Interface : http://localhost:8501

## Lancer avec Docker

```bash
docker compose up --build
```
Puis ouvrez http://localhost:8501. Le backend est accessible séparément sur http://localhost:8000/docs.

Arrêter : `docker compose down`

## Tests

```bash
pip install -r requirements-dev.txt
pytest backend/tests/ -v
```
16 tests couvrant le module d'inférence (chargement du modèle, cohérence des prédictions, robustesse à l'ordre des colonnes) et l'API (validation des entrées, gestion des erreurs, endpoint batch).

CI/CD : le workflow GitHub Actions (`.github/workflows/ci.yml`) relance cette suite à chaque push.

## Structure du projet

```
fraud-detection-app/
├── notebooks/
│   └── 01_exploration_et_modelisation.ipynb
├── data/                      # creditcard.csv (non versionné, voir Kaggle)
├── models/                    # artefacts générés par le notebook
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py            # routes FastAPI
│   │   ├── inference.py       # chargement modèle + prédiction
│   │   └── schemas.py         # validation Pydantic
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   └── app.py                 # dashboard Streamlit
├── docker-compose.yml
├── requirements-backend.txt
├── requirements-frontend.txt
└── requirements-dev.txt
```

## Limites connues

- Modèle entraîné sur des données de 2013 (transactions européennes) — un recalibrage serait nécessaire avant tout usage réel
- Le stockage du modèle est local (fichiers `.joblib`) : pas de registre de modèles versionné (MLflow, etc.)
- Pas d'authentification sur l'API — à ajouter avant toute exposition publique avec des données sensibles réelles

---
*Projet portfolio — non destiné à un usage en production sans validation métier complémentaire.*


https://detection-desfraudes-bancaires-ml.onrender.com
https://front-detection-fraude-ml-sup.onrender.com