"""Analytics controller: model diagnostics, feature analysis, segmentation, AI insights."""
import os
import pandas as pd
from flask import Blueprint, render_template, jsonify, flash, redirect, url_for, current_app, request
from werkzeug.utils import secure_filename
from sqlalchemy import func, case

from app.config import Config
from app.constants import ALL_FEATURES, TARGET
from app.extensions import db
from app.models import Customer, Province
from app.routes.helpers import login_required
from app.ml import predictor

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
@login_required
def index():
    meta = predictor.get_metadata() if predictor.model_available() else None
    return render_template("analytics.html", meta=meta, model_ready=predictor.model_available())


@analytics_bp.route("/analytics/train", methods=["POST"])
@login_required
def train_model():
    try:
        from app.ml.train import train
        bundle = train(verbose=False)
        predictor.load_bundle(force=True)
        flash(f"Model trained. Best model: {bundle['best_model']} "
              f"(AUC {bundle['metrics'][bundle['best_model']]['roc_auc']}).", "success")
    except FileNotFoundError:
        flash("Dataset not found. Run generate_dataset.py first.", "danger")
    except Exception as exc:
        current_app.logger.exception("Training failed")
        flash(f"Training failed: {exc}", "danger")
    return redirect(url_for("analytics.index"))


@analytics_bp.route("/analytics/upload-csv", methods=["POST"])
@login_required
def upload_csv():
    """Upload CSV, validate, save to DB, and retrain model."""
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
        missing = set(ALL_FEATURES + [TARGET]) - set(df.columns)
        if missing:
            return jsonify({"error": f"Missing columns: {', '.join(missing)}"}), 400

        # clear existing customers
        db.session.query(Customer).delete()
        db.session.commit()

        # insert new customers
        province_map = {p.province_name: p.province_id for p in Province.query.all()}
        records = []
        for _, row in df.iterrows():
            prov_name = row.get("province_name")
            if prov_name not in province_map:
                continue
            records.append({
                "age": int(row["age"]),
                "gender": row["gender"],
                "province_id": province_map[prov_name],
                "area_type": row["area_type"],
                "network_quality": row["network_quality"],
                "internet_type": row["internet_type"],
                "call_drop_rate": float(row["call_drop_rate"]),
                "recharge_amount": float(row["recharge_amount"]),
                "recharge_frequency": int(row["recharge_frequency"]),
                "payment_method": row["payment_method"],
                "tenure_months": int(row["tenure_months"]),
                "inactive_days": int(row["inactive_days"]),
                "complaint_count": int(row["complaint_count"]),
                "tower_availability": row["tower_availability"],
                "competitor_offer_exposure": row["competitor_offer_exposure"],
                "discount_usage": row["discount_usage"],
                "churn": int(row["churn"]),
            })
        db.session.bulk_insert_mappings(Customer, records)
        db.session.commit()

        # save CSV to dataset path for training
        os.makedirs(Config.DATASET_DIR, exist_ok=True)
        df.to_csv(Config.DATASET_PATH, index=False)

        # retrain model
        from app.ml.train import train
        bundle = train(verbose=False)
        predictor.load_bundle(force=True)

        return jsonify({
            "success": True,
            "message": f"Imported {len(records)} customers. Model retrained: {bundle['best_model']} (AUC {bundle['metrics'][bundle['best_model']]['roc_auc']})."
        })
    except Exception as exc:
        current_app.logger.exception("CSV upload failed")
        return jsonify({"error": str(exc)}), 500


@analytics_bp.route("/api/analytics/model")
@login_required
def api_model():
    if not predictor.model_available():
        return jsonify({"error": "Model not trained"}), 400
    return jsonify(predictor.get_metadata())


@analytics_bp.route("/api/analytics/feature-importance")
@login_required
def api_feature_importance():
    if not predictor.model_available():
        return jsonify({"labels": [], "values": []})
    fi = predictor.get_metadata()["feature_importance"][:12]
    return jsonify({
        "labels": [x["feature"] for x in fi],
        "values": [x["importance"] for x in fi],
    })


@analytics_bp.route("/api/analytics/province")
@login_required
def api_province():
    rows = (
        db.session.query(
            Province.province_name,
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .join(Customer, Customer.province_id == Province.province_id)
        .group_by(Province.province_name)
        .all()
    )
    data = [{
        "province": n, "customers": int(t or 0),
        "churn_rate": round((int(c or 0) / int(t or 1)) * 100, 1),
    } for n, t, c in rows]
    data.sort(key=lambda x: x["churn_rate"], reverse=True)
    return jsonify(data)


@analytics_bp.route("/api/analytics/complaints")
@login_required
def api_complaints():
    # churn rate grouped by complaint count bucket
    buckets = [(0, 0), (1, 1), (2, 2), (3, 4), (5, 100)]
    labels, values = [], []
    for lo, hi in buckets:
        q = db.session.query(
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        ).filter(Customer.complaint_count >= lo, Customer.complaint_count <= hi)
        total, churned = q.one()
        total = int(total or 0)
        churned = int(churned or 0)
        labels.append(f"{lo}" if lo == hi else (f"{lo}+" if hi == 100 else f"{lo}-{hi}"))
        values.append(round((churned / total * 100) if total else 0, 1))
    return jsonify({"labels": labels, "values": values})


@analytics_bp.route("/api/analytics/segmentation")
@login_required
def api_segmentation():
    # segment by tenure groups
    segs = [("New (0-6m)", 0, 6), ("Growing (7-18m)", 7, 18),
            ("Mature (19-48m)", 19, 48), ("Loyal (49m+)", 49, 1000)]
    out = []
    for name, lo, hi in segs:
        total = db.session.query(func.count(Customer.customer_id)).filter(
            Customer.tenure_months >= lo, Customer.tenure_months <= hi).scalar() or 0
        out.append({"segment": name, "count": int(total)})
    return jsonify({"labels": [s["segment"] for s in out], "values": [s["count"] for s in out]})


@analytics_bp.route("/api/analytics/top-risk")
@login_required
def api_top_risk():
    # heuristic risk among non-churned customers (no per-row inference for 15k)
    risk_expr = (
        Customer.complaint_count * 8
        + Customer.inactive_days * 0.4
        + Customer.call_drop_rate * 2
        - Customer.recharge_frequency * 2
        + case((Customer.competitor_offer_exposure == "Yes", 15), else_=0)
    ).label("risk")
    rows = (
        db.session.query(Customer, risk_expr)
        .filter(Customer.churn == 0)
        .order_by(risk_expr.desc())
        .limit(10)
        .all()
    )
    data = []
    for cust, risk in rows:
        data.append({
            "customer_id": cust.customer_id,
            "province": cust.province.province_name if cust.province else "-",
            "complaints": cust.complaint_count,
            "inactive_days": cust.inactive_days,
            "recharge_amount": cust.recharge_amount,
            "competitor": cust.competitor_offer_exposure,
            "risk_score": round(float(risk), 1),
        })
    return jsonify(data)


@analytics_bp.route("/api/analytics/heatmap")
@login_required
def api_heatmap():
    # churn rate by province x network quality
    rows = (
        db.session.query(
            Province.province_name,
            Customer.network_quality,
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .join(Customer, Customer.province_id == Province.province_id)
        .group_by(Province.province_name, Customer.network_quality)
        .all()
    )
    cells = {}
    provinces = set()
    for prov, net, total, churned in rows:
        provinces.add(prov)
        cells[(prov, net)] = round((int(churned or 0) / int(total or 1)) * 100, 1)
    nets = ["Poor", "Average", "Good", "Excellent"]
    provinces = sorted(provinces)
    matrix = [[cells.get((p, n), 0) for n in nets] for p in provinces]
    return jsonify({"provinces": provinces, "networks": nets, "matrix": matrix})


@analytics_bp.route("/api/analytics/ai-insights")
@login_required
def api_ai_insights():
    """Generate AI-powered business insights from analytics data."""
    insights = []
    
    # Insight 1: High complaints churn correlation
    high_complaint_churn = (
        db.session.query(
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .filter(Customer.complaint_count >= 5)
        .one()
    )
    hc_total, hc_churned = high_complaint_churn
    hc_total = int(hc_total or 0)
    hc_churned = int(hc_churned or 0)
    hc_rate = round((hc_churned / hc_total * 100) if hc_total else 0, 1)
    insights.append({
        "icon": "bi-chat-dots",
        "title": "Complaint Impact",
        "text": f"Customers with 5+ complaints churn at {hc_rate}%. High complaint volume is a critical churn indicator.",
        "severity": "high" if hc_rate > 50 else "medium",
    })
    
    # Insight 2: Inactive days correlation
    inactive_churn = (
        db.session.query(
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .filter(Customer.inactive_days >= 45)
        .one()
    )
    inc_total, inc_churned = inactive_churn
    inc_total = int(inc_total or 0)
    inc_churned = int(inc_churned or 0)
    inc_rate = round((inc_churned / inc_total * 100) if inc_total else 0, 1)
    insights.append({
        "icon": "bi-clock-history",
        "title": "Inactivity Risk",
        "text": f"Customers inactive for 45+ days churn at {inc_rate}%. Re-engagement campaigns needed for dormant users.",
        "severity": "high" if inc_rate > 60 else "medium",
    })
    
    # Insight 3: Network quality impact
    poor_network_churn = (
        db.session.query(
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .filter(Customer.network_quality == "Poor")
        .one()
    )
    pn_total, pn_churned = poor_network_churn
    pn_total = int(pn_total or 0)
    pn_churned = int(pn_churned or 0)
    pn_rate = round((pn_churned / pn_total * 100) if pn_total else 0, 1)
    insights.append({
        "icon": "bi-broadcast-pin",
        "title": "Network Quality",
        "text": f"Customers with Poor network quality churn at {pn_rate}%. Tower infrastructure upgrades in low-coverage areas recommended.",
        "severity": "high" if pn_rate > 50 else "medium",
    })
    
    # Insight 4: Recharge frequency correlation
    low_recharge_churn = (
        db.session.query(
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .filter(Customer.recharge_frequency <= 2)
        .one()
    )
    lr_total, lr_churned = low_recharge_churn
    lr_total = int(lr_total or 0)
    lr_churned = int(lr_churned or 0)
    lr_rate = round((lr_churned / lr_total * 100) if lr_total else 0, 1)
    insights.append({
        "icon": "bi-wallet2",
        "title": "Recharge Frequency",
        "text": f"Customers with low recharge frequency (≤2/month) churn at {lr_rate}%. Incentivize more frequent recharges.",
        "severity": "high" if lr_rate > 50 else "medium",
    })
    
    # Insight 5: Top risk province
    province_rows = (
        db.session.query(
            Province.province_name,
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .join(Customer, Customer.province_id == Province.province_id)
        .group_by(Province.province_name)
        .all()
    )
    prov_data = []
    for name, total, churned in province_rows:
        total = int(total or 0)
        churned = int(churned or 0)
        prov_data.append({
            "province": name,
            "churn_rate": round((churned / total * 100) if total else 0, 1),
        })
    prov_data.sort(key=lambda x: x["churn_rate"], reverse=True)
    top_province = prov_data[0] if prov_data else None
    if top_province:
        insights.append({
            "icon": "bi-geo-alt",
            "title": "Regional Risk",
            "text": f"{top_province['province']} has the highest churn rate at {top_province['churn_rate']}%. Prioritize retention campaigns in this region.",
            "severity": "high" if top_province["churn_rate"] > 40 else "medium",
        })
    
    # Insight 6: Competitor exposure impact
    competitor_churn = (
        db.session.query(
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .filter(Customer.competitor_offer_exposure == "Yes")
        .one()
    )
    comp_total, comp_churned = competitor_churn
    comp_total = int(comp_total or 0)
    comp_churned = int(comp_churned or 0)
    comp_rate = round((comp_churned / comp_total * 100) if comp_total else 0, 1)
    insights.append({
        "icon": "bi-shield-shaded",
        "title": "Competitor Pressure",
        "text": f"Competitor-exposed customers churn at {comp_rate}%. Proactive loyalty offers needed to counter competitor offers.",
        "severity": "high" if comp_rate > 50 else "medium",
    })
    
    return jsonify(insights)


# ======================================================================
# Model Diagnostics (read-only; never retrains)
# ======================================================================
@analytics_bp.route("/analytics/model-diagnostics")
@login_required
def model_diagnostics():
    return render_template(
        "model_diagnostics.html", model_ready=predictor.model_available()
    )


@analytics_bp.route("/api/analytics/diagnostics")
@login_required
def api_diagnostics():
    if not predictor.model_available():
        return jsonify({"error": "Model not trained yet"}), 404
    try:
        from app.ml.diagnostics import compute_diagnostics
        return jsonify(compute_diagnostics())
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:  # pragma: no cover
        current_app.logger.exception("Diagnostics failed")
        return jsonify({"error": str(exc)}), 500


# ======================================================================
# Real-Time Data Viewer + Live Database Monitor
# ======================================================================
@analytics_bp.route("/analytics/live-data")
@login_required
def live_data():
    return render_template("live_data.html")


@analytics_bp.route("/api/analytics/live-data")
@login_required
def api_live_data():
    """Newest records across the deployed system for the real-time viewer."""
    from app.models import PredictionLog, RecommendationLog, CustomerRiskHistory

    latest_customers = (
        Customer.query.join(Province).order_by(Customer.customer_id.desc()).limit(10).all()
    )
    latest_predictions = (
        PredictionLog.query.order_by(PredictionLog.created_at.desc()).limit(10).all()
    )
    latest_recs = (
        RecommendationLog.query.order_by(RecommendationLog.created_at.desc()).limit(10).all()
    )
    latest_risk = (
        CustomerRiskHistory.query.order_by(CustomerRiskHistory.recorded_at.desc()).limit(10).all()
    )

    return jsonify({
        "latest_customers": [
            {"customer_id": c.customer_id,
             "province": c.province.province_name if c.province else None,
             "gender": c.gender, "age": c.age,
             "network_quality": c.network_quality,
             "health_score": c.health_score(),
             "health_status": c.health_status()}
            for c in latest_customers
        ],
        "latest_predictions": [p.to_dict() for p in latest_predictions],
        "latest_recommendations": [r.to_dict() for r in latest_recs],
        "latest_risk_scores": [
            {"id": r.id, "customer_id": r.customer_id, "risk_score": r.risk_score,
             "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None}
            for r in latest_risk
        ],
    })


@analytics_bp.route("/api/analytics/db-monitor")
@login_required
def api_db_monitor():
    """Aggregate counters for the live database monitor."""
    from datetime import datetime, timedelta
    from app.models import PredictionLog, RecommendationLog, CustomerRiskHistory

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=7)

    total_customers = db.session.query(func.count(Customer.customer_id)).scalar() or 0

    def _safe_count(model, time_col=None, since=None):
        try:
            q = db.session.query(func.count(model.id))
            if time_col is not None and since is not None:
                q = q.filter(time_col >= since)
            return q.scalar() or 0
        except Exception:
            return 0

    total_predictions = _safe_count(PredictionLog)
    total_recommendations = _safe_count(RecommendationLog)
    total_high_risk = 0
    try:
        total_high_risk = (
            db.session.query(func.count(func.distinct(PredictionLog.customer_id)))
            .filter(PredictionLog.risk_level == "High").scalar() or 0
        )
    except Exception:
        total_high_risk = 0

    customers_today = (
        db.session.query(func.count(CustomerRiskHistory.id))
        .filter(CustomerRiskHistory.recorded_at >= today_start).scalar() or 0
    )
    predictions_today = _safe_count(PredictionLog, PredictionLog.created_at, today_start)
    predictions_week = _safe_count(PredictionLog, PredictionLog.created_at, week_start)

    return jsonify({
        "total_customers": int(total_customers),
        "total_predictions": int(total_predictions),
        "total_high_risk": int(total_high_risk),
        "total_recommendations": int(total_recommendations),
        "records_added_today": int(predictions_today + customers_today),
        "records_added_this_week": int(predictions_week),
    })
