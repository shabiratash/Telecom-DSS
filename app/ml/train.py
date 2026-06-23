"""
Train and compare four churn models (Random Forest, Decision Tree,
Logistic Regression, XGBoost), pick the best by ROC-AUC / F1, and persist
the full bundle (preprocessing + model + metrics + diagnostics) to
models_ml/churn_model.pkl via joblib.
"""
import os
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
    roc_auc_score,
)

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except Exception:  # pragma: no cover
    HAS_XGB = False

from app.config import Config
from app.constants import NUMERIC_FEATURES, CATEGORICAL_FEATURES, ALL_FEATURES, TARGET


def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def candidate_models():
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=220, max_depth=14, min_samples_leaf=4,
            n_jobs=-1, random_state=42, class_weight="balanced_subsample"
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=10, min_samples_leaf=20, random_state=42, class_weight="balanced"
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=2000, C=1.0, class_weight="balanced"
        ),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.08,
            subsample=0.9, colsample_bytree=0.9, eval_metric="logloss",
            random_state=42, n_jobs=-1, tree_method="hist",
        )
    return models


def _feature_names(preprocessor):
    cat = preprocessor.named_transformers_["cat"]
    cat_names = list(cat.get_feature_names_out(CATEGORICAL_FEATURES))
    return list(NUMERIC_FEATURES) + cat_names


def _importance(model, feature_names):
    if hasattr(model, "feature_importances_"):
        vals = model.feature_importances_
    elif hasattr(model, "coef_"):
        vals = np.abs(model.coef_).ravel()
    else:
        return []
    pairs = sorted(zip(feature_names, vals), key=lambda x: x[1], reverse=True)
    # collapse one-hot back to base feature for readability
    agg = {}
    for name, val in pairs:
        base = name
        for c in CATEGORICAL_FEATURES:
            if name.startswith(c + "_"):
                base = c
                break
        agg[base] = agg.get(base, 0.0) + float(val)
    total = sum(agg.values()) or 1.0
    out = [{"feature": k, "importance": round(v / total, 4)} for k, v in
           sorted(agg.items(), key=lambda x: x[1], reverse=True)]
    return out


def train(dataset_path=None, verbose=True):
    dataset_path = dataset_path or Config.DATASET_PATH
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Run generate_dataset.py first."
        )

    df = pd.read_csv(dataset_path)
    X = df[ALL_FEATURES].copy()
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results = {}
    fitted = {}
    for name, clf in candidate_models().items():
        pipe = Pipeline([("prep", build_preprocessor()), ("clf", clf)])
        pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)

        metrics = {
            "accuracy": round(accuracy_score(y_test, pred), 4),
            "precision": round(precision_score(y_test, pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, pred, zero_division=0), 4),
            "f1": round(f1_score(y_test, pred, zero_division=0), 4),
            "roc_auc": round(roc_auc_score(y_test, proba), 4),
        }
        results[name] = metrics
        fitted[name] = pipe
        if verbose:
            print(f"{name:20s} | acc={metrics['accuracy']} f1={metrics['f1']} auc={metrics['roc_auc']}")

    # pick best by roc_auc then f1
    best_name = max(results, key=lambda n: (results[n]["roc_auc"], results[n]["f1"]))
    best_pipe = fitted[best_name]

    # diagnostics for the best model
    proba = best_pipe.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    cm = confusion_matrix(y_test, pred).tolist()
    fpr, tpr, _ = roc_curve(y_test, proba)
    # downsample ROC to <= 100 points
    idx = np.linspace(0, len(fpr) - 1, min(100, len(fpr))).astype(int)
    roc = {"fpr": fpr[idx].round(4).tolist(), "tpr": tpr[idx].round(4).tolist()}

    prep = best_pipe.named_steps["prep"]
    feat_names = _feature_names(prep)
    importance = _importance(best_pipe.named_steps["clf"], feat_names)

    bundle = {
        "pipeline": best_pipe,
        "best_model": best_name,
        "metrics": results,
        "confusion_matrix": cm,
        "roc_curve": roc,
        "feature_importance": importance,
        "features": ALL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "churn_rate": round(float(y.mean()), 4),
        "n_samples": int(len(df)),
    }

    os.makedirs(Config.ML_MODEL_DIR, exist_ok=True)
    joblib.dump(bundle, Config.ML_MODEL_PATH)
    if verbose:
        print(f"\nBest model: {best_name} -> saved to {Config.ML_MODEL_PATH}")
    return bundle


if __name__ == "__main__":
    train()
