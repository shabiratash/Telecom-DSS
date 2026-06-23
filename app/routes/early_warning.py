"""Early Warning System controller: track risk changes and generate alerts."""
from flask import Blueprint, render_template, jsonify
from sqlalchemy import func, case
from datetime import datetime, timedelta

from app.extensions import db
from app.models import Customer, CustomerRiskHistory
from app.routes.helpers import login_required
from app.ml import predictor

early_warning_bp = Blueprint("early_warning", __name__)


@early_warning_bp.route("/early-warning")
@login_required
def index():
    return render_template("early_warning.html", model_ready=predictor.model_available())


@early_warning_bp.route("/api/early-warning/alerts")
@login_required
def api_alerts():
    """Get customers with significant risk increase (alerts)."""
    threshold = 20  # Risk increase threshold in percentage points
    
    # Get customers with recent risk history
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    # Calculate current risk for all non-churned customers
    from sqlalchemy import case as sql_case
    risk_expr = (
        Customer.complaint_count * 8
        + Customer.inactive_days * 0.4
        + Customer.call_drop_rate * 2
        - Customer.recharge_frequency * 2
        + sql_case((Customer.competitor_offer_exposure == "Yes", 15), else_=0)
    ).label("current_risk")
    
    # Get customers with risk history
    customers_with_history = (
        db.session.query(Customer, risk_expr)
        .filter(Customer.churn == 0)
        .filter(Customer.customer_id.in_(
            db.session.query(CustomerRiskHistory.customer_id)
            .filter(CustomerRiskHistory.recorded_at >= cutoff_date)
            .distinct()
        ))
        .all()
    )
    
    alerts = []
    for cust, current_risk in customers_with_history:
        # Get previous risk from history
        previous = (
            db.session.query(CustomerRiskHistory)
            .filter(CustomerRiskHistory.customer_id == cust.customer_id)
            .filter(CustomerRiskHistory.recorded_at >= cutoff_date)
            .order_by(CustomerRiskHistory.recorded_at.desc())
            .first()
        )
        
        if previous:
            risk_increase = current_risk - previous.risk_score
            if risk_increase >= threshold:
                # Determine alert level
                if risk_increase >= 50:
                    alert_level = "Critical"
                elif risk_increase >= 35:
                    alert_level = "High"
                else:
                    alert_level = "Medium"
                
                alerts.append({
                    "customer_id": cust.customer_id,
                    "province": cust.province.province_name if cust.province else "-",
                    "previous_risk": round(previous.risk_score, 1),
                    "current_risk": round(current_risk, 1),
                    "risk_increase": round(risk_increase, 1),
                    "alert_level": alert_level,
                    "recorded_at": previous.recorded_at.strftime("%Y-%m-%d %H:%M"),
                })
    
    # Sort by risk increase descending
    alerts.sort(key=lambda x: x["risk_increase"], reverse=True)
    
    return jsonify(alerts[:20])  # Return top 20 alerts


@early_warning_bp.route("/api/early-warning/recent-warnings")
@login_required
def api_recent_warnings():
    """Get recent warnings from risk history."""
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    # Get recent risk history entries with significant changes
    history = (
        db.session.query(CustomerRiskHistory, Customer)
        .join(Customer, Customer.customer_id == CustomerRiskHistory.customer_id)
        .filter(CustomerRiskHistory.recorded_at >= cutoff_date)
        .order_by(CustomerRiskHistory.recorded_at.desc())
        .limit(50)
        .all()
    )
    
    warnings = []
    for risk_hist, cust in history:
        warnings.append({
            "customer_id": cust.customer_id,
            "province": cust.province.province_name if cust.province else "-",
            "risk_score": round(risk_hist.risk_score, 1),
            "recorded_at": risk_hist.recorded_at.strftime("%Y-%m-%d %H:%M"),
        })
    
    return jsonify(warnings)


@early_warning_bp.route("/api/early-warning/top-risk")
@login_required
def api_top_risk():
    """Get top risk customers for trend analysis."""
    from sqlalchemy import case as sql_case
    risk_expr = (
        Customer.complaint_count * 8
        + Customer.inactive_days * 0.4
        + Customer.call_drop_rate * 2
        - Customer.recharge_frequency * 2
        + sql_case((Customer.competitor_offer_exposure == "Yes", 15), else_=0)
    ).label("risk")
    
    rows = (
        db.session.query(Customer, risk_expr)
        .filter(Customer.churn == 0)
        .order_by(risk_expr.desc())
        .limit(15)
        .all()
    )
    
    data = []
    for cust, risk in rows:
        # Get risk history for this customer
        history = (
            db.session.query(CustomerRiskHistory)
            .filter(CustomerRiskHistory.customer_id == cust.customer_id)
            .order_by(CustomerRiskHistory.recorded_at.desc())
            .limit(10)
            .all()
        )
        
        risk_trend = [{"risk": round(h.risk_score, 1), "date": h.recorded_at.strftime("%Y-%m-%d")} for h in history]
        
        data.append({
            "customer_id": cust.customer_id,
            "province": cust.province.province_name if cust.province else "-",
            "current_risk": round(risk, 1),
            "risk_trend": risk_trend,
        })
    
    return jsonify(data)


@early_warning_bp.route("/api/early-warning/record-risk", methods=["POST"])
@login_required
def record_risk():
    """Record current risk scores for all customers (scheduled task)."""
    from sqlalchemy import case as sql_case
    risk_expr = (
        Customer.complaint_count * 8
        + Customer.inactive_days * 0.4
        + Customer.call_drop_rate * 2
        - Customer.recharge_frequency * 2
        + sql_case((Customer.competitor_offer_exposure == "Yes", 15), else_=0)
    ).label("risk")
    
    rows = (
        db.session.query(Customer.customer_id, risk_expr)
        .all()
    )
    
    # Insert risk history records
    records = []
    for customer_id, risk in rows:
        records.append({
            "customer_id": customer_id,
            "risk_score": float(risk),
            "recorded_at": datetime.utcnow(),
        })
    
    db.session.bulk_insert_mappings(CustomerRiskHistory, records)
    db.session.commit()
    
    return jsonify({"success": True, "recorded": len(records)})
