"""Customer management controller: list, search, filter, paginate, CRUD, profile."""
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
)
from sqlalchemy import or_, func

from app.extensions import db
from app.models import (
    Customer, Province, CustomerRiskHistory, PredictionLog, RecommendationLog,
)
from app.routes.helpers import login_required
from app.constants import (
    GENDERS, AREA_TYPES, NETWORK_QUALITY, INTERNET_TYPES,
    PAYMENT_METHODS, TOWER_AVAILABILITY, YES_NO,
)
from app.ml import predictor
from app.services import logging_service

customer_bp = Blueprint("customer", __name__)


FORM_FIELDS = {
    "age": int, "gender": str, "province_id": int, "area_type": str,
    "network_quality": str, "internet_type": str, "call_drop_rate": float,
    "recharge_amount": float, "recharge_frequency": int, "payment_method": str,
    "tenure_months": int, "inactive_days": int, "complaint_count": int,
    "tower_availability": str, "competitor_offer_exposure": str,
    "discount_usage": str, "churn": int,
}


def _form_options():
    return {
        "provinces": Province.query.order_by(Province.province_name).all(),
        "genders": GENDERS, "area_types": AREA_TYPES,
        "network_quality": NETWORK_QUALITY, "internet_types": INTERNET_TYPES,
        "payment_methods": PAYMENT_METHODS, "tower_availability": TOWER_AVAILABILITY,
        "yes_no": YES_NO,
    }


def _parse_form(form):
    data, errors = {}, []
    for field, caster in FORM_FIELDS.items():
        raw = form.get(field)
        if raw is None or raw == "":
            if field == "churn":
                data[field] = 0
                continue
            errors.append(f"{field} is required")
            continue
        try:
            data[field] = caster(raw)
        except (ValueError, TypeError):
            errors.append(f"{field} has an invalid value")
    
    # Additional validation
    if "age" in data and (data["age"] < 18 or data["age"] > 70):
        errors.append("Age must be between 18 and 70")
    if "call_drop_rate" in data and (data["call_drop_rate"] < 0 or data["call_drop_rate"] > 20):
        errors.append("Call drop rate must be between 0 and 20")
    if "recharge_amount" in data and (data["recharge_amount"] < 50 or data["recharge_amount"] > 5000):
        errors.append("Recharge amount must be between 50 and 5000 AFN")
    if "recharge_frequency" in data and (data["recharge_frequency"] < 1 or data["recharge_frequency"] > 30):
        errors.append("Recharge frequency must be between 1 and 30")
    if "tenure_months" in data and (data["tenure_months"] < 1 or data["tenure_months"] > 120):
        errors.append("Tenure must be between 1 and 120 months")
    if "inactive_days" in data and (data["inactive_days"] < 0 or data["inactive_days"] > 90):
        errors.append("Inactive days must be between 0 and 90")
    if "complaint_count" in data and (data["complaint_count"] < 0 or data["complaint_count"] > 20):
        errors.append("Complaint count must be between 0 and 20")
    
    return data, errors


@customer_bp.route("/customers")
@login_required
def list_customers():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ITEMS_PER_PAGE"]
    search = request.args.get("search", "", type=str).strip()
    province_id = request.args.get("province_id", type=int)
    churn = request.args.get("churn", type=str)
    network = request.args.get("network_quality", type=str)

    query = Customer.query.join(Province)
    if search:
        like = f"%{search}%"
        conds = [Province.province_name.ilike(like), Customer.gender.ilike(like)]
        if search.isdigit():
            conds.append(Customer.customer_id == int(search))
        query = query.filter(or_(*conds))
    if province_id:
        query = query.filter(Customer.province_id == province_id)
    if churn in ("0", "1"):
        query = query.filter(Customer.churn == int(churn))
    if network:
        query = query.filter(Customer.network_quality == network)

    pagination = query.order_by(Customer.customer_id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "customers.html",
        pagination=pagination,
        customers=pagination.items,
        options=_form_options(),
        filters={"search": search, "province_id": province_id, "churn": churn, "network_quality": network},
    )


@customer_bp.route("/customers/add", methods=["GET", "POST"])
@login_required
def add_customer():
    if request.method == "POST":
        data, errors = _parse_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("customer_workspace/add.html", options=_form_options(), form=request.form)
        customer = Customer(**data)
        db.session.add(customer)
        db.session.commit()
        flash(f"Customer #{customer.customer_id} added successfully.", "success")
        return redirect(url_for("customer.profile_full", customer_id=customer.customer_id))
    return render_template("customer_workspace/add.html", options=_form_options(), form={})


@customer_bp.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == "POST":
        data, errors = _parse_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("customer_workspace/edit.html", customer=customer, options=_form_options())
        for k, v in data.items():
            setattr(customer, k, v)
        db.session.commit()
        flash(f"Customer #{customer_id} updated.", "success")
        return redirect(url_for("customer.profile_full", customer_id=customer_id))
    return render_template("customer_workspace/edit.html", customer=customer, options=_form_options())


@customer_bp.route("/customers/<int:customer_id>/delete", methods=["POST"])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash(f"Customer #{customer_id} deleted.", "info")
    return redirect(url_for("customer.list_customers"))


def _predict_and_log(customer, source):
    """Run a prediction for a saved customer and log it (guarded). Returns result or None."""
    if not predictor.model_available():
        return None
    try:
        result = predictor.predict(customer.feature_dict())
        result["health_score"] = customer.health_score()
        result["health_status"] = customer.health_status()
        logging_service.log_prediction(result, customer_id=customer.customer_id, source=source)
        return result
    except Exception as exc:  # pragma: no cover
        current_app.logger.warning("Prediction failed: %s", exc)
        return None


@customer_bp.route("/customers/<int:customer_id>")
@login_required
def profile(customer_id):
    # Backward-compatible: redirect the legacy profile URL to the rich workspace profile.
    return redirect(url_for("customer.profile_full", customer_id=customer_id))


@customer_bp.route("/customers/view/<int:customer_id>")
@login_required
def view(customer_id):
    """Read-only customer details page (no prediction trigger)."""
    customer = Customer.query.get_or_404(customer_id)
    return render_template("customer_workspace/view.html", customer=customer)


@customer_bp.route("/customers/profile/<int:customer_id>")
@login_required
def profile_full(customer_id):
    """Rich CRM customer profile with prediction, health, and history timelines."""
    customer = Customer.query.get_or_404(customer_id)
    prediction = _predict_and_log(customer, source="profile")
    return render_template(
        "customer_workspace/profile.html",
        customer=customer,
        prediction=prediction,
    )


# ----------------------------------------------------------------------
# Customer Workspace sub-pages
# ----------------------------------------------------------------------
@customer_bp.route("/customers/prediction-history")
@login_required
def prediction_history():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ITEMS_PER_PAGE"]
    pagination = (
        PredictionLog.query.order_by(PredictionLog.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template(
        "customer_workspace/prediction_history.html",
        pagination=pagination, logs=pagination.items,
    )


@customer_bp.route("/customers/risk-history")
@login_required
def risk_history():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ITEMS_PER_PAGE"]
    pagination = (
        CustomerRiskHistory.query.order_by(CustomerRiskHistory.recorded_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template(
        "customer_workspace/risk_history.html",
        pagination=pagination, logs=pagination.items,
    )


@customer_bp.route("/customers/recommendations")
@login_required
def recommendations():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ITEMS_PER_PAGE"]
    pagination = (
        RecommendationLog.query.order_by(RecommendationLog.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template(
        "customer_workspace/recommendations.html",
        pagination=pagination, logs=pagination.items,
    )


@customer_bp.route("/customers/health-scores")
@login_required
def health_scores():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["ITEMS_PER_PAGE"]
    pagination = (
        Customer.query.join(Province).order_by(Customer.customer_id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template(
        "customer_workspace/health_scores.html",
        pagination=pagination, customers=pagination.items,
    )


@customer_bp.route("/customers/live-monitor")
@login_required
def live_monitor():
    return render_template("customer_workspace/live_monitor.html")


# ----------------------------------------------------------------------
# Workspace JSON APIs (used by live monitor + profile timelines)
# ----------------------------------------------------------------------
@customer_bp.route("/api/customers/live-monitor")
@login_required
def api_live_monitor():
    """Aggregated live feed for the customer workspace monitor."""
    latest_customers = (
        Customer.query.join(Province).order_by(Customer.customer_id.desc()).limit(8).all()
    )
    latest_predictions = (
        PredictionLog.query.order_by(PredictionLog.created_at.desc()).limit(8).all()
    )
    latest_recs = (
        RecommendationLog.query.order_by(RecommendationLog.created_at.desc()).limit(8).all()
    )
    latest_risk = (
        CustomerRiskHistory.query.order_by(CustomerRiskHistory.recorded_at.desc()).limit(8).all()
    )

    high_risk = [
        {
            "customer_id": c.customer_id,
            "province": c.province.province_name if c.province else None,
            "health_score": c.health_score(),
            "health_status": c.health_status(),
        }
        for c in latest_customers if c.health_status() in ("Critical", "Warning")
    ]

    return jsonify({
        "new_customers": [
            {
                "customer_id": c.customer_id,
                "province": c.province.province_name if c.province else None,
                "gender": c.gender,
                "age": c.age,
                "health_score": c.health_score(),
                "health_status": c.health_status(),
            } for c in latest_customers
        ],
        "recent_predictions": [p.to_dict() for p in latest_predictions],
        "recent_recommendations": [r.to_dict() for r in latest_recs],
        "recent_risk": [
            {"id": r.id, "customer_id": r.customer_id, "risk_score": r.risk_score,
             "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None}
            for r in latest_risk
        ],
        "high_risk": high_risk,
    })


@customer_bp.route("/api/customers/<int:customer_id>/prediction-history")
@login_required
def api_customer_prediction_history(customer_id):
    logs = (
        PredictionLog.query.filter_by(customer_id=customer_id)
        .order_by(PredictionLog.created_at.asc()).limit(100).all()
    )
    return jsonify([p.to_dict() for p in logs])


@customer_bp.route("/api/customers/<int:customer_id>/recommendation-history")
@login_required
def api_customer_recommendation_history(customer_id):
    logs = (
        RecommendationLog.query.filter_by(customer_id=customer_id)
        .order_by(RecommendationLog.created_at.desc()).limit(100).all()
    )
    return jsonify([r.to_dict() for r in logs])


@customer_bp.route("/api/customers/<int:customer_id>/risk-history")
@login_required
def api_customer_risk_history(customer_id):
    logs = (
        CustomerRiskHistory.query.filter_by(customer_id=customer_id)
        .order_by(CustomerRiskHistory.recorded_at.asc()).limit(100).all()
    )
    return jsonify([
        {"id": r.id, "risk_score": r.risk_score,
         "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None}
        for r in logs
    ])
