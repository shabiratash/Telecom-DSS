"""Financial Impact controller: calculate revenue risk from churn."""
from flask import Blueprint, render_template, jsonify
from sqlalchemy import func, case

from app.extensions import db
from app.models import Customer, Province
from app.routes.helpers import login_required
from app.ml import predictor

financial_bp = Blueprint("financial", __name__)


@financial_bp.route("/financial-impact")
@login_required
def index():
    return render_template("financial_impact.html", model_ready=predictor.model_available())


@financial_bp.route("/api/financial/summary")
@login_required
def api_summary():
    """Calculate financial impact summary."""
    # Calculate high risk customers (risk score > 50)
    from sqlalchemy import case as sql_case
    risk_expr = (
        Customer.complaint_count * 8
        + Customer.inactive_days * 0.4
        + Customer.call_drop_rate * 2
        - Customer.recharge_frequency * 2
        + sql_case((Customer.competitor_offer_exposure == "Yes", 15), else_=0)
    ).label("risk")
    
    # High risk threshold
    high_risk_threshold = 50
    
    # Get all non-churned customers with risk scores
    rows = (
        db.session.query(Customer, risk_expr)
        .filter(Customer.churn == 0)
        .all()
    )
    
    high_risk_customers = []
    total_recharge = 0
    high_risk_recharge = 0
    
    for cust, risk in rows:
        if risk >= high_risk_threshold:
            high_risk_customers.append(cust.customer_id)
            high_risk_recharge += cust.recharge_amount or 0
        total_recharge += cust.recharge_amount or 0
    
    # Calculate averages
    total_customers = len(rows)
    high_risk_count = len(high_risk_customers)
    avg_recharge = total_recharge / total_customers if total_customers else 0
    high_risk_avg_recharge = high_risk_recharge / high_risk_count if high_risk_count else 0
    
    # Calculate potential revenue loss
    monthly_loss = high_risk_avg_recharge * high_risk_count
    yearly_loss = monthly_loss * 12
    
    # Calculate province-wise revenue risk
    province_risk = (
        db.session.query(
            Province.province_name,
            func.count(Customer.customer_id),
            func.sum(Customer.recharge_amount),
            func.sum(Customer.churn),
        )
        .join(Customer, Customer.province_id == Province.province_id)
        .group_by(Province.province_name)
        .all()
    )
    
    province_data = []
    for name, total, recharge, churned in province_risk:
        total = int(total or 0)
        recharge = float(recharge or 0)
        churned = int(churned or 0)
        churn_rate = (churned / total * 100) if total else 0
        avg_recharge = recharge / total if total else 0
        potential_loss = avg_recharge * (total - churned) * (churn_rate / 100) * 12  # Yearly potential loss
        province_data.append({
            "province": name,
            "total_customers": total,
            "avg_recharge": round(avg_recharge, 2),
            "churn_rate": round(churn_rate, 1),
            "yearly_risk": round(potential_loss, 2),
        })
    
    province_data.sort(key=lambda x: x["yearly_risk"], reverse=True)
    
    return jsonify({
        "high_risk_customers": high_risk_count,
        "total_customers": total_customers,
        "avg_recharge": round(avg_recharge, 2),
        "high_risk_avg_recharge": round(high_risk_avg_recharge, 2),
        "monthly_loss": round(monthly_loss, 2),
        "yearly_loss": round(yearly_loss, 2),
        "province_risk": province_data[:15],
    })


@financial_bp.route("/api/financial/province-breakdown")
@login_required
def api_province_breakdown():
    """Get detailed province revenue risk breakdown."""
    province_risk = (
        db.session.query(
            Province.province_name,
            func.count(Customer.customer_id),
            func.sum(Customer.recharge_amount),
            func.sum(Customer.churn),
        )
        .join(Customer, Customer.province_id == Province.province_id)
        .group_by(Province.province_name)
        .all()
    )
    
    data = []
    for name, total, recharge, churned in province_risk:
        total = int(total or 0)
        recharge = float(recharge or 0)
        churned = int(churned or 0)
        churn_rate = (churned / total * 100) if total else 0
        avg_recharge = recharge / total if total else 0
        active_customers = total - churned
        monthly_revenue = avg_recharge * active_customers
        yearly_revenue = monthly_revenue * 12
        monthly_risk = monthly_revenue * (churn_rate / 100)
        yearly_risk = yearly_revenue * (churn_rate / 100)
        
        data.append({
            "province": name,
            "total_customers": total,
            "active_customers": active_customers,
            "churned_customers": churned,
            "churn_rate": round(churn_rate, 1),
            "avg_recharge": round(avg_recharge, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "yearly_revenue": round(yearly_revenue, 2),
            "monthly_risk": round(monthly_risk, 2),
            "yearly_risk": round(yearly_risk, 2),
        })
    
    data.sort(key=lambda x: x["yearly_risk"], reverse=True)
    return jsonify(data)
