"""What-If Simulator controller: simulate feature changes and their impact on churn probability."""
from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import func

from app.extensions import db
from app.models import Customer, Province
from app.routes.helpers import login_required
from app.ml import predictor
from app.constants import NETWORK_QUALITY, YES_NO

whatif_bp = Blueprint("whatif_simulator", __name__)


@whatif_bp.route("/what-if-simulator")
@login_required
def index():
    """What-If Simulator main page."""
    customers = Customer.query.order_by(Customer.customer_id.desc()).limit(100).all()
    return render_template("whatif_simulator/index.html", customers=customers)


@whatif_bp.route("/api/whatif/customers")
@login_required
def api_customers():
    """API endpoint to get customer list for dropdown."""
    customers = Customer.query.order_by(Customer.customer_id.desc()).limit(200).all()
    return jsonify([{
        "customer_id": c.customer_id,
        "name": f"Customer #{c.customer_id}",
        "province": c.province.province_name if c.province else "Unknown",
    } for c in customers])


@whatif_bp.route("/api/whatif/customer/<int:customer_id>")
@login_required
def api_customer_details(customer_id):
    """API endpoint to get customer details for simulation."""
    customer = Customer.query.get_or_404(customer_id)
    features = customer.feature_dict()
    
    # Get current prediction
    if not predictor.model_available():
        return jsonify({"error": "Model not trained"}), 400
    
    current_result = predictor.predict(features)
    
    return jsonify({
        "customer_id": customer.customer_id,
        "features": features,
        "current_prediction": current_result,
    })


@whatif_bp.route("/api/whatif/simulate", methods=["POST"])
@login_required
def api_simulate():
    """API endpoint to simulate prediction with modified features."""
    if not predictor.model_available():
        return jsonify({"error": "Model not trained"}), 400
    
    data = request.get_json()
    customer_id = data.get("customer_id")
    modified_features = data.get("features", {})
    
    # Get original customer data
    customer = Customer.query.get_or_404(customer_id)
    original_features = customer.feature_dict()
    
    # Apply modifications
    for key, value in modified_features.items():
        original_features[key] = value
    
    # Get predictions
    original_result = predictor.predict(customer.feature_dict())
    new_result = predictor.predict(original_features)
    
    # Calculate improvement
    improvement = original_result["probability"] - new_result["probability"]
    
    # Calculate impact percentages for each changed feature
    impacts = []
    for key in modified_features.keys():
        original_value = customer.feature_dict().get(key)
        new_value = modified_features.get(key)
        
        # Simulate changing only this feature
        test_features = customer.feature_dict().copy()
        test_features[key] = new_value
        test_result = predictor.predict(test_features)
        
        feature_impact = original_result["probability"] - test_result["probability"]
        impacts.append({
            "feature": key,
            "original": original_value,
            "new": new_value,
            "impact": round(feature_impact, 2),
        })
    
    return jsonify({
        "current_probability": original_result["probability"],
        "new_probability": new_result["probability"],
        "improvement": round(improvement, 2),
        "current_risk": original_result["risk_level"],
        "new_risk": new_result["risk_level"],
        "impacts": impacts,
    })
