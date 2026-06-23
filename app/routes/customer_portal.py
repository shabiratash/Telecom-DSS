"""Customer Portal: dedicated customer interface for personal predictions and insights."""
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from app.routes.helpers import login_required
from app.models.customer import Customer
from app.ml.predictor import predict, model_available

customer_portal_bp = Blueprint("customer_portal", __name__, url_prefix="/customer-portal")


@customer_portal_bp.route("/")
@login_required
def home():
    """Customer portal home/dashboard."""
    if session.get("role") != "customer":
        flash("Access denied. Customer portal only.", "danger")
        return redirect(url_for("dashboard.index"))
    
    # Get customer-specific data (for demo, use first customer)
    customer = Customer.query.first()
    
    return render_template(
        "customer_portal/home.html",
        customer=customer,
        model_available=model_available()
    )


@customer_portal_bp.route("/prediction")
@login_required
def prediction():
    """Personal churn prediction page."""
    if session.get("role") != "customer":
        flash("Access denied. Customer portal only.", "danger")
        return redirect(url_for("dashboard.index"))
    
    customer = Customer.query.first()
    prediction_result = None
    
    if customer and model_available():
        try:
            prediction_result = predict(customer.feature_dict())
        except Exception as e:
            flash(f"Prediction error: {str(e)}", "danger")
    
    return render_template(
        "customer_portal/prediction.html",
        customer=customer,
        prediction=prediction_result,
        model_available=model_available()
    )


@customer_portal_bp.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    """API endpoint for live prediction from form data."""
    if session.get("role") != "customer":
        return jsonify({"error": "Access denied"}), 403
    
    if not model_available():
        return jsonify({"error": "Model not available"}), 503
    
    try:
        data = request.json
        features = {
            "age": int(data.get("age", 30)),
            "gender": data.get("gender", "Male"),
            "province_name": data.get("province_name", "Kabul"),
            "area_type": data.get("area_type", "Urban"),
            "network_quality": data.get("network_quality", "Good"),
            "internet_type": data.get("internet_type", "4G"),
            "call_drop_rate": float(data.get("call_drop_rate", 0)),
            "recharge_amount": float(data.get("recharge_amount", 100)),
            "recharge_frequency": int(data.get("recharge_frequency", 4)),
            "payment_method": data.get("payment_method", "Cash"),
            "tenure_months": int(data.get("tenure_months", 12)),
            "inactive_days": int(data.get("inactive_days", 0)),
            "complaint_count": int(data.get("complaint_count", 0)),
            "tower_availability": data.get("tower_availability", "High"),
            "competitor_offer_exposure": data.get("competitor_offer_exposure", "No"),
            "discount_usage": data.get("discount_usage", "No"),
        }
        result = predict(features)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customer_portal_bp.route("/risk-status")
@login_required
def risk_status():
    """Risk status and health score page."""
    if session.get("role") != "customer":
        flash("Access denied. Customer portal only.", "danger")
        return redirect(url_for("dashboard.index"))
    
    customer = Customer.query.first()
    
    return render_template(
        "customer_portal/risk_status.html",
        customer=customer
    )


@customer_portal_bp.route("/recommendations")
@login_required
def recommendations():
    """Personalized recommendations page."""
    if session.get("role") != "customer":
        flash("Access denied. Customer portal only.", "danger")
        return redirect(url_for("dashboard.index"))
    
    customer = Customer.query.first()
    prediction_result = None
    
    if customer and model_available():
        try:
            prediction_result = predict(customer.feature_dict())
        except Exception as e:
            flash(f"Prediction error: {str(e)}", "danger")
    
    return render_template(
        "customer_portal/recommendations.html",
        customer=customer,
        prediction=prediction_result,
        model_available=model_available()
    )


@customer_portal_bp.route("/profile")
@login_required
def profile():
    """Customer profile information page."""
    if session.get("role") != "customer":
        flash("Access denied. Customer portal only.", "danger")
        return redirect(url_for("dashboard.index"))
    
    customer = Customer.query.first()
    
    return render_template(
        "customer_portal/profile.html",
        customer=customer
    )


@customer_portal_bp.route("/live-data")
@login_required
def live_data():
    """Real-time data viewer for customer portal."""
    if session.get("role") != "customer":
        flash("Access denied. Customer portal only.", "danger")
        return redirect(url_for("dashboard.index"))
    
    return render_template("customer_portal/live_data.html")


@customer_portal_bp.route("/api/live-data")
@login_required
def api_live_data():
    """API endpoint for live data."""
    if session.get("role") != "customer":
        return jsonify({"error": "Access denied"}), 403
    
    try:
        # Get latest customer data
        latest_customer = Customer.query.order_by(Customer.customer_id.desc()).first()
        
        # Get customer count
        total_customers = Customer.query.count()
        
        # Get churn count
        churned_count = Customer.query.filter_by(churn=1).count()
        
        # Get health stats
        customers = Customer.query.all()
        health_scores = [c.health_score() for c in customers]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
        
        return jsonify({
            "latest_customer": latest_customer.to_dict() if latest_customer else None,
            "stats": {
                "total_customers": total_customers,
                "churned_count": churned_count,
                "churn_rate": round((churned_count / total_customers * 100), 2) if total_customers > 0 else 0,
                "avg_health_score": round(avg_health, 1)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
