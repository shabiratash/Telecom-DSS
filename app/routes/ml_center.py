"""Machine Learning Center controller: dataset overview, training, model comparison, history."""
import os
import pandas as pd
import joblib
from flask import Blueprint, render_template, jsonify, send_file, flash, redirect, url_for
from datetime import datetime

from app.config import Config
from app.extensions import db
from app.models import ModelTrainingHistory
from app.routes.helpers import login_required
from app.ml import train
from app.constants import ALL_FEATURES, TARGET

ml_center_bp = Blueprint("ml_center", __name__)


def _get_dataset_info():
    """Get dataset overview information."""
    dataset_path = Config.DATASET_PATH
    if not os.path.exists(dataset_path):
        return None
    
    df = pd.read_csv(dataset_path)
    total_records = len(df)
    feature_count = len(ALL_FEATURES)
    target_column = TARGET
    missing_values = df[ALL_FEATURES].isnull().sum().sum()
    train_test_ratio = "80:20"  # Fixed split in train.py
    
    return {
        "total_records": total_records,
        "feature_count": feature_count,
        "target_column": target_column,
        "missing_values": int(missing_values),
        "train_test_ratio": train_test_ratio,
        "dataset_path": dataset_path,
    }


def _get_model_bundle():
    """Load the trained model bundle if available."""
    if not os.path.exists(Config.ML_MODEL_PATH):
        return None
    try:
        return joblib.load(Config.ML_MODEL_PATH)
    except Exception:
        return None


@ml_center_bp.route("/machine-learning")
@login_required
def index():
    """ML Center main page."""
    dataset_info = _get_dataset_info()
    model_bundle = _get_model_bundle()
    model_history = ModelTrainingHistory.query.order_by(ModelTrainingHistory.training_date.desc()).limit(20).all()
    
    return render_template(
        "ml_center/index.html",
        dataset_info=dataset_info,
        model_bundle=model_bundle,
        model_history=model_history,
    )


@ml_center_bp.route("/api/ml-center/dataset")
@login_required
def api_dataset():
    """API endpoint for dataset overview."""
    info = _get_dataset_info()
    if info is None:
        return jsonify({"error": "Dataset not found"}), 404
    return jsonify(info)


@ml_center_bp.route("/api/ml-center/train", methods=["POST"])
@login_required
def api_train():
    """Trigger model training and save results to history."""
    try:
        # Train the model using existing train function
        bundle = train.train(verbose=False)
        
        # Save all model results to history
        best_model_name = bundle["best_model"]
        metrics = bundle["metrics"]
        
        # Clear previous best model flag
        ModelTrainingHistory.query.update({"is_best_model": False})
        db.session.commit()
        
        # Save each model's results
        for model_name, model_metrics in metrics.items():
            history = ModelTrainingHistory(
                model_name=model_name,
                accuracy=model_metrics["accuracy"],
                precision_score=model_metrics["precision"],
                recall_score=model_metrics["recall"],
                f1_score=model_metrics["f1"],
                is_best_model=(model_name == best_model_name),
            )
            db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "best_model": best_model_name,
            "metrics": metrics,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ml_center_bp.route("/api/ml-center/model-comparison")
@login_required
def api_model_comparison():
    """API endpoint for model comparison metrics."""
    bundle = _get_model_bundle()
    if bundle is None:
        return jsonify({"error": "Model not trained yet"}), 404
    
    metrics = bundle["metrics"]
    comparison = []
    for model_name, model_metrics in metrics.items():
        comparison.append({
            "model": model_name,
            "accuracy": model_metrics["accuracy"],
            "precision": model_metrics["precision"],
            "recall": model_metrics["recall"],
            "f1": model_metrics["f1"],
            "roc_auc": model_metrics.get("roc_auc", 0),
        })
    
    return jsonify(comparison)


@ml_center_bp.route("/api/ml-center/confusion-matrix")
@login_required
def api_confusion_matrix():
    """API endpoint for confusion matrix."""
    bundle = _get_model_bundle()
    if bundle is None:
        return jsonify({"error": "Model not trained yet"}), 404
    
    return jsonify({
        "confusion_matrix": bundle["confusion_matrix"],
        "best_model": bundle["best_model"],
    })


@ml_center_bp.route("/api/ml-center/roc-curve")
@login_required
def api_roc_curve():
    """API endpoint for ROC curve data."""
    bundle = _get_model_bundle()
    if bundle is None:
        return jsonify({"error": "Model not trained yet"}), 404
    
    return jsonify({
        "fpr": bundle["roc_curve"]["fpr"],
        "tpr": bundle["roc_curve"]["tpr"],
        "best_model": bundle["best_model"],
    })


@ml_center_bp.route("/api/ml-center/feature-importance")
@login_required
def api_feature_importance():
    """API endpoint for feature importance."""
    bundle = _get_model_bundle()
    if bundle is None:
        return jsonify({"error": "Model not trained yet"}), 404
    
    return jsonify({
        "feature_importance": bundle["feature_importance"],
        "best_model": bundle["best_model"],
    })


@ml_center_bp.route("/api/ml-center/best-model")
@login_required
def api_best_model():
    """API endpoint for best model information."""
    bundle = _get_model_bundle()
    if bundle is None:
        return jsonify({"error": "Model not trained yet"}), 404
    
    best_name = bundle["best_model"]
    best_metrics = bundle["metrics"][best_name]
    
    # Get training date from history
    history_entry = ModelTrainingHistory.query.filter_by(
        model_name=best_name, is_best_model=True
    ).first()
    
    return jsonify({
        "model_name": best_name,
        "accuracy": best_metrics["accuracy"],
        "precision": best_metrics["precision"],
        "recall": best_metrics["recall"],
        "f1": best_metrics["f1"],
        "roc_auc": best_metrics.get("roc_auc", 0),
        "training_date": history_entry.training_date.isoformat() if history_entry else None,
        "n_samples": bundle.get("n_samples", 0),
        "churn_rate": bundle.get("churn_rate", 0),
    })


@ml_center_bp.route("/api/ml-center/history")
@login_required
def api_history():
    """API endpoint for model training history."""
    history = ModelTrainingHistory.query.order_by(ModelTrainingHistory.training_date.desc()).limit(50).all()
    return jsonify([h.to_dict() for h in history])


@ml_center_bp.route("/machine-learning/download-model")
@login_required
def download_model():
    """Download the trained model file."""
    if not os.path.exists(Config.ML_MODEL_PATH):
        flash("Model file not found. Train the model first.", "danger")
        return redirect(url_for("ml_center.index"))
    
    return send_file(
        Config.ML_MODEL_PATH,
        as_attachment=True,
        download_name="churn_model.pkl",
        mimetype="application/octet-stream"
    )
