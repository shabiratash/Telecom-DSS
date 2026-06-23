"""
Model diagnostics (READ-ONLY).

This module NEVER trains or refits a model. It loads the already-trained
pipeline from churn_model.pkl and evaluates it (predict-only) against the same
deterministic train/validation/test split used at training time
(train_test_split with random_state=42, stratify=y), to surface an
overfitting signal (Train accuracy - Test accuracy gap).

Because the pipeline was fit on the 80% training partition, the "Train" and
"Validation" partitions here are drawn from data the model has seen; the
meaningful overfitting comparison is Train (seen) vs Test (unseen holdout).
"""
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
)

from app.config import Config
from app.constants import ALL_FEATURES, TARGET
from app.ml import predictor


def _status_for_gap(gap_pct):
    if gap_pct < 5:
        return "Healthy", "success"
    if gap_pct <= 10:
        return "Warning", "warning"
    return "Potential Overfitting", "danger"


def compute_diagnostics():
    """Return overfitting + performance diagnostics for the deployed model.

    Raises FileNotFoundError if the model or dataset is missing.
    """
    bundle = predictor.load_bundle()
    pipe = bundle["pipeline"]

    dataset_path = Config.DATASET_PATH
    if not os.path.exists(dataset_path):
        raise FileNotFoundError("Dataset not found; cannot compute diagnostics.")

    df = pd.read_csv(dataset_path)
    X = df[ALL_FEATURES].copy()
    y = df[TARGET].astype(int)

    # Recreate the exact split used in ml/train.py (no refit happens here).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    # Carve a validation slice from the training partition for reporting.
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.25, random_state=42, stratify=y_train
    )

    def _acc(X_part, y_part):
        if len(X_part) == 0:
            return 0.0
        pred = (pipe.predict_proba(X_part)[:, 1] >= 0.5).astype(int)
        return round(accuracy_score(y_part, pred) * 100, 2)

    train_acc = _acc(X_tr, y_tr)
    val_acc = _acc(X_val, y_val)
    test_acc = _acc(X_test, y_test)

    gap = round(train_acc - test_acc, 2)
    status, severity = _status_for_gap(gap)

    # Test-set performance metrics (recomputed predict-only for consistency).
    proba_test = pipe.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= 0.5).astype(int)
    performance = {
        "accuracy": round(accuracy_score(y_test, pred_test) * 100, 2),
        "precision": round(precision_score(y_test, pred_test, zero_division=0) * 100, 2),
        "recall": round(recall_score(y_test, pred_test, zero_division=0) * 100, 2),
        "f1": round(f1_score(y_test, pred_test, zero_division=0) * 100, 2),
        "roc_auc": round(roc_auc_score(y_test, proba_test) * 100, 2),
    }

    # Confusion matrix (TN, FP, FN, TP) on the test holdout.
    tp = int(((pred_test == 1) & (y_test.values == 1)).sum())
    tn = int(((pred_test == 0) & (y_test.values == 0)).sum())
    fp = int(((pred_test == 1) & (y_test.values == 0)).sum())
    fn = int(((pred_test == 0) & (y_test.values == 1)).sum())
    confusion = [[tn, fp], [fn, tp]]

    # Prefer the ROC curve already stored in the bundle; fall back to recompute.
    roc = bundle.get("roc_curve")
    if not roc:
        from sklearn.metrics import roc_curve
        fpr, tpr, _ = roc_curve(y_test, proba_test)
        idx = np.linspace(0, len(fpr) - 1, min(100, len(fpr))).astype(int)
        roc = {"fpr": fpr[idx].round(4).tolist(), "tpr": tpr[idx].round(4).tolist()}

    return {
        "best_model": bundle.get("best_model"),
        "n_samples": int(len(df)),
        "split": {"train": int(len(X_tr)), "validation": int(len(X_val)), "test": int(len(X_test))},
        "overfitting": {
            "train_accuracy": train_acc,
            "validation_accuracy": val_acc,
            "test_accuracy": test_acc,
            "gap": gap,
            "status": status,
            "severity": severity,
        },
        "performance": performance,
        "confusion_matrix": confusion,
        "roc_curve": roc,
        "note": (
            "Read-only diagnostics. The existing trained model is evaluated "
            "predict-only against the deterministic train/val/test split; no "
            "retraining occurs."
        ),
    }
