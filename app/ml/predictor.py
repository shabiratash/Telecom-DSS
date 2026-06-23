"""Model loading + churn prediction service."""
import os
import threading
import joblib
import pandas as pd

from app.config import Config
from app.constants import ALL_FEATURES
from app.ml.recommendations import generate_recommendations

_lock = threading.Lock()
_bundle = None


def _generate_reasons(features: dict, probability: float) -> list:
    """Generate specific reasons for churn prediction based on feature values."""
    reasons = []
    
    complaints = features.get("complaint_count", 0) or 0
    inactive = features.get("inactive_days", 0) or 0
    rfreq = features.get("recharge_frequency", 0) or 0
    competitor = str(features.get("competitor_offer_exposure", "No"))
    discount = str(features.get("discount_usage", "No"))
    drop = features.get("call_drop_rate", 0) or 0
    network = str(features.get("network_quality", "Good"))
    tenure = features.get("tenure_months", 0) or 0
    recharge = features.get("recharge_amount", 0) or 0
    
    if complaints >= 5:
        reasons.append(f"High complaint count ({complaints}) indicates dissatisfaction")
    elif complaints >= 3:
        reasons.append(f"Elevated complaints ({complaints}) suggest service issues")
    
    if inactive >= 45:
        reasons.append(f"Very high inactivity ({inactive} days) - customer disengaged")
    elif inactive >= 30:
        reasons.append(f"Extended inactivity ({inactive} days) - risk of leaving")
    
    if rfreq <= 2:
        reasons.append(f"Low recharge frequency ({rfreq}/month) - poor engagement")
    elif rfreq <= 4:
        reasons.append(f"Below-average recharge frequency ({rfreq}/month)")
    
    if competitor == "Yes":
        reasons.append("Exposed to competitor offers - vulnerable to switching")
    
    if drop >= 12:
        reasons.append(f"Very high call drop rate ({drop}%) - poor network quality")
    elif drop >= 8:
        reasons.append(f"Elevated call drop rate ({drop}%) - network issues")
    
    if network == "Poor":
        reasons.append("Poor network quality - major churn driver")
    elif network == "Average":
        reasons.append("Average network quality - could be improved")
    
    if tenure <= 6:
        reasons.append(f"New customer ({tenure} months) - early-stage churn risk")
    elif tenure <= 12:
        reasons.append(f"Short tenure ({tenure} months) - not yet established loyalty")
    
    if recharge < 100:
        reasons.append(f"Low spend profile ({recharge} AFN) - may seek better value")
    
    if discount == "No":
        reasons.append("Not using discounts - missing retention incentives")
    
    if not reasons:
        reasons.append("Overall churn risk based on combined factors")
    
    return reasons


def load_bundle(force=False):
    """Lazily load (and cache) the trained model bundle."""
    global _bundle
    with _lock:
        if _bundle is None or force:
            if not os.path.exists(Config.ML_MODEL_PATH):
                raise FileNotFoundError(
                    "Trained model not found. Run `python -m ml.train` first."
                )
            _bundle = joblib.load(Config.ML_MODEL_PATH)
    return _bundle


def model_available():
    return os.path.exists(Config.ML_MODEL_PATH)


def get_metadata():
    """Return metrics/diagnostics without the heavy pipeline object."""
    b = load_bundle()
    return {
        "best_model": b.get("best_model"),
        "metrics": b.get("metrics"),
        "confusion_matrix": b.get("confusion_matrix"),
        "roc_curve": b.get("roc_curve"),
        "feature_importance": b.get("feature_importance"),
        "churn_rate": b.get("churn_rate"),
        "n_samples": b.get("n_samples"),
    }


def risk_level(prob: float) -> str:
    if prob >= 0.66:
        return "High"
    if prob >= 0.33:
        return "Medium"
    return "Low"


def _calculate_feature_contributions(features: dict, prob: float) -> list:
    """Calculate estimated contribution of each feature to the prediction."""
    contributions = []
    
    # Get feature importance from the model bundle
    b = load_bundle()
    feature_importance = b.get("feature_importance", [])
    
    # Create a mapping of feature names to importance scores
    importance_map = {fi["feature"]: fi["importance"] for fi in feature_importance}
    
    # Calculate contribution based on feature importance and value
    complaints = features.get("complaint_count", 0) or 0
    inactive = features.get("inactive_days", 0) or 0
    rfreq = features.get("recharge_frequency", 0) or 0
    competitor = str(features.get("competitor_offer_exposure", "No"))
    discount = str(features.get("discount_usage", "No"))
    drop = features.get("call_drop_rate", 0) or 0
    network = str(features.get("network_quality", "Good"))
    tenure = features.get("tenure_months", 0) or 0
    recharge = features.get("recharge_amount", 0) or 0
    
    # Calculate weighted contributions
    total_importance = sum(importance_map.values()) or 1.0
    
    # Complaint count contribution
    if complaints > 0:
        complaint_contrib = (importance_map.get("complaint_count", 0.1) / total_importance) * min(complaints / 10, 1.0) * 100
        contributions.append({"feature": "Complaint Count", "value": complaints, "contribution": round(complaint_contrib, 1)})
    
    # Inactive days contribution
    if inactive > 0:
        inactive_contrib = (importance_map.get("inactive_days", 0.1) / total_importance) * min(inactive / 60, 1.0) * 100
        contributions.append({"feature": "Inactive Days", "value": inactive, "contribution": round(inactive_contrib, 1)})
    
    # Network quality contribution
    network_scores = {"Poor": 1.0, "Average": 0.6, "Good": 0.3, "Excellent": 0.1}
    network_contrib = (importance_map.get("network_quality", 0.1) / total_importance) * network_scores.get(network, 0.3) * 100
    contributions.append({"feature": "Network Quality", "value": network, "contribution": round(network_contrib, 1)})
    
    # Recharge frequency contribution
    if rfreq > 0:
        rfreq_contrib = (importance_map.get("recharge_frequency", 0.1) / total_importance) * (1 - min(rfreq / 10, 1.0)) * 100
        contributions.append({"feature": "Recharge Frequency", "value": rfreq, "contribution": round(rfreq_contrib, 1)})
    
    # Call drop rate contribution
    if drop > 0:
        drop_contrib = (importance_map.get("call_drop_rate", 0.1) / total_importance) * min(drop / 20, 1.0) * 100
        contributions.append({"feature": "Call Drop Rate", "value": drop, "contribution": round(drop_contrib, 1)})
    
    # Competitor offer contribution
    if competitor == "Yes":
        competitor_contrib = (importance_map.get("competitor_offer_exposure", 0.05) / total_importance) * 100
        contributions.append({"feature": "Competitor Offer", "value": competitor, "contribution": round(competitor_contrib, 1)})
    
    # Discount usage contribution (negative contribution if not using)
    if discount == "No":
        discount_contrib = (importance_map.get("discount_usage", 0.05) / total_importance) * 100
        contributions.append({"feature": "Discount Usage", "value": discount, "contribution": round(discount_contrib, 1)})
    
    # Sort by contribution
    contributions.sort(key=lambda x: x["contribution"], reverse=True)
    
    # Normalize to 100%
    total_contrib = sum(c["contribution"] for c in contributions) or 100
    for c in contributions:
        c["contribution"] = round((c["contribution"] / total_contrib) * 100, 1)
    
    # Add "Other Factors" if total is less than 100
    if contributions:
        current_total = sum(c["contribution"] for c in contributions)
        if current_total < 100:
            contributions.append({
                "feature": "Other Factors",
                "value": "-",
                "contribution": round(100 - current_total, 1)
            })
    
    return contributions[:8]  # Return top 8 factors


def predict(features: dict):
    """
    Predict churn for a single feature dict.
    Returns dict with prediction, probability, risk_level, reasons, recommendations, feature_contributions.
    """
    b = load_bundle()
    pipe = b["pipeline"]
    row = {f: features.get(f) for f in ALL_FEATURES}
    X = pd.DataFrame([row])
    prob = float(pipe.predict_proba(X)[:, 1][0])
    pred = int(prob >= 0.5)
    return {
        "prediction": pred,
        "prediction_label": "Customer will Churn" if pred == 1 else "Customer will Stay",
        "probability": round(prob * 100, 2),
        "risk_level": risk_level(prob),
        "reasons": _generate_reasons(features, prob),
        "recommendations": generate_recommendations(features, prob),
        "feature_contributions": _calculate_feature_contributions(features, prob),
    }


def predict_batch(feature_dicts):
    b = load_bundle()
    pipe = b["pipeline"]
    rows = [{f: fd.get(f) for f in ALL_FEATURES} for fd in feature_dicts]
    X = pd.DataFrame(rows)
    probs = pipe.predict_proba(X)[:, 1]
    out = []
    for fd, p in zip(feature_dicts, probs):
        p = float(p)
        out.append({
            "probability": round(p * 100, 2),
            "prediction": int(p >= 0.5),
            "risk_level": risk_level(p),
        })
    return out
