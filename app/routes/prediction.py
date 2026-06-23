"""Churn prediction controller + model management."""
import os
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, flash, current_app, send_file
from werkzeug.utils import secure_filename

from app.config import Config
from app.extensions import db
from app.models import Province, Customer
from app.routes.helpers import login_required
from app.constants import (
    GENDERS, AREA_TYPES, NETWORK_QUALITY, INTERNET_TYPES,
    PAYMENT_METHODS, TOWER_AVAILABILITY, YES_NO, ALL_FEATURES,
)
from app.ml import predictor
from app.services import logging_service

prediction_bp = Blueprint("prediction", __name__)


def _options():
    return {
        "provinces": Province.query.order_by(Province.province_name).all(),
        "genders": GENDERS, "area_types": AREA_TYPES,
        "network_quality": NETWORK_QUALITY, "internet_types": INTERNET_TYPES,
        "payment_methods": PAYMENT_METHODS, "tower_availability": TOWER_AVAILABILITY,
        "yes_no": YES_NO,
    }


def _extract_features(src):
    casts = {
        "age": int, "call_drop_rate": float, "recharge_amount": float,
        "recharge_frequency": int, "tenure_months": int, "inactive_days": int,
        "complaint_count": int,
    }
    feats = {}
    for f in ALL_FEATURES:
        raw = src.get(f)
        if f in casts and raw not in (None, ""):
            try:
                feats[f] = casts[f](raw)
            except (ValueError, TypeError):
                feats[f] = 0
        else:
            feats[f] = raw
    return feats


@prediction_bp.route("/prediction", methods=["GET", "POST"])
@login_required
def predict_page():
    result = None
    form = {}
    if request.method == "POST":
        form = request.form.to_dict()
        if not predictor.model_available():
            flash("Model not trained yet. Train it from the Analytics page.", "warning")
        else:
            feats = _extract_features(request.form)
            try:
                result = predictor.predict(feats)
                # Calculate health score from features
                temp_customer = Customer(**feats)
                result["health_score"] = temp_customer.health_score()
                result["health_status"] = temp_customer.health_status()
                # Audit log (guarded; never breaks prediction)
                logging_service.log_prediction(result, customer_id=None, source="single")
            except Exception as exc:
                current_app.logger.exception("Prediction error")
                flash(f"Prediction failed: {exc}", "danger")
    return render_template(
        "prediction.html", options=_options(), result=result, form=form,
        model_ready=predictor.model_available(),
    )


@prediction_bp.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    if not predictor.model_available():
        return jsonify({"error": "Model not trained"}), 400
    payload = request.get_json(silent=True) or request.form.to_dict()
    feats = _extract_features(payload)
    try:
        result = predictor.predict(feats)
        # Save customer data to database
        province_map = {p.province_name: p.province_id for p in Province.query.all()}
        prov_name = payload.get("province_name")
        province_id = province_map.get(prov_name) if prov_name else None
        
        if province_id:
            customer = Customer(
                age=int(payload.get("age", 0)),
                gender=payload.get("gender"),
                province_id=province_id,
                area_type=payload.get("area_type"),
                network_quality=payload.get("network_quality"),
                internet_type=payload.get("internet_type"),
                call_drop_rate=float(payload.get("call_drop_rate", 0)),
                recharge_amount=float(payload.get("recharge_amount", 0)),
                recharge_frequency=int(payload.get("recharge_frequency", 0)),
                payment_method=payload.get("payment_method"),
                tenure_months=int(payload.get("tenure_months", 0)),
                inactive_days=int(payload.get("inactive_days", 0)),
                complaint_count=int(payload.get("complaint_count", 0)),
                tower_availability=payload.get("tower_availability"),
                competitor_offer_exposure=payload.get("competitor_offer_exposure"),
                discount_usage=payload.get("discount_usage"),
                churn=1 if result.get("prediction_label") == "Churn" else 0,
            )
            db.session.add(customer)
            db.session.commit()
            result["customer_id"] = customer.customer_id
            logging_service.log_prediction(result, customer_id=customer.customer_id, source="api")
        else:
            logging_service.log_prediction(result, customer_id=None, source="api")
        return jsonify(result)
    except Exception as exc:
        current_app.logger.exception("Prediction error")
        return jsonify({"error": str(exc)}), 500


@prediction_bp.route("/prediction/batch-predict", methods=["POST"])
@login_required
def batch_predict():
    """Upload CSV, predict churn for all rows, return results CSV."""
    if not predictor.model_available():
        return jsonify({"error": "Model not trained"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "File must be a CSV"}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(Config.UPLOAD_DIR, filename)
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    file.save(upload_path)

    try:
        df = pd.read_csv(upload_path)
        # validate required columns
        missing = set(ALL_FEATURES) - set(df.columns)
        if missing:
            return jsonify({"error": f"Missing columns: {', '.join(missing)}"}), 400

        # map province_name to province_id for prediction
        province_map = {p.province_name: p.province_id for p in Province.query.all()}
        df["province_id"] = df.get("province_name", "").map(province_map)
        df["province_id"] = df["province_id"].fillna(0).astype(int)

        # run predictions
        predictions = []
        for _, row in df.iterrows():
            feats = _extract_features(row.to_dict())
            try:
                pred = predictor.predict(feats)
                predictions.append({
                    "churn_probability": pred.get("probability", 0),
                    "risk_level": pred.get("risk_level", "Unknown"),
                    "prediction_label": pred.get("prediction_label", "Unknown"),
                })
            except Exception:
                predictions.append({
                    "churn_probability": 0,
                    "risk_level": "Unknown",
                    "prediction_label": "Unknown",
                })

        pred_df = pd.DataFrame(predictions)
        result_df = pd.concat([df, pred_df], axis=1)

        # Audit log every batch prediction (guarded; never breaks the response)
        logging_service.log_predictions_bulk(
            ((p, None) for p in predictions), source="batch"
        )

        # save result
        output_path = os.path.join(Config.UPLOAD_DIR, f"predicted_{filename}")
        result_df.to_csv(output_path, index=False)

        return jsonify({
            "success": True,
            "message": f"Predicted {len(result_df)} records",
            "download_url": f"/prediction/download/{filename}"
        })
    except Exception as exc:
        current_app.logger.exception("Batch prediction failed")
        return jsonify({"error": str(exc)}), 500


@prediction_bp.route("/prediction/download/<filename>")
@login_required
def download_prediction(filename):
    """Download the predicted CSV file."""
    safe_name = secure_filename(filename)
    output_path = os.path.join(Config.UPLOAD_DIR, f"predicted_{safe_name}")
    if not os.path.exists(output_path):
        return "File not found", 404
    return send_file(output_path, as_attachment=True, download_name=f"predicted_{safe_name}")
