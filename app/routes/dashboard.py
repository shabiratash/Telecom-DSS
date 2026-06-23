"""Dashboard controller: KPIs, province stats and chart data."""
from flask import Blueprint, render_template, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models import Customer, Province
from app.routes.helpers import login_required
from app.ml import predictor

dashboard_bp = Blueprint("dashboard", __name__)


def _kpis():
    total = db.session.query(func.count(Customer.customer_id)).scalar() or 0
    churned = db.session.query(func.count(Customer.customer_id)).filter(Customer.churn == 1).scalar() or 0
    active = total - churned
    avg_recharge = db.session.query(func.avg(Customer.recharge_amount)).scalar() or 0
    avg_complaints = db.session.query(func.avg(Customer.complaint_count)).scalar() or 0
    churn_rate = (churned / total * 100) if total else 0
    return {
        "total": total,
        "churned": churned,
        "active": active,
        "avg_recharge": round(float(avg_recharge), 2),
        "avg_complaints": round(float(avg_complaints), 2),
        "churn_rate": round(churn_rate, 2),
        "provinces": db.session.query(func.count(Province.province_id)).scalar() or 0,
    }


@dashboard_bp.route("/dashboard")
@login_required
def index():
    return render_template("dashboard.html", kpis=_kpis(), model_ready=predictor.model_available())


@dashboard_bp.route("/api/dashboard/summary")
@login_required
def api_summary():
    return jsonify(_kpis())


@dashboard_bp.route("/api/dashboard/churn-split")
@login_required
def api_churn_split():
    k = _kpis()
    return jsonify({"labels": ["Active", "Churned"], "values": [k["active"], k["churned"]]})


@dashboard_bp.route("/api/dashboard/province-customers")
@login_required
def api_province_customers():
    rows = (
        db.session.query(Province.province_name, func.count(Customer.customer_id))
        .join(Customer, Customer.province_id == Province.province_id)
        .group_by(Province.province_name)
        .order_by(func.count(Customer.customer_id).desc())
        .limit(15)
        .all()
    )
    return jsonify({"labels": [r[0] for r in rows], "values": [int(r[1]) for r in rows]})


@dashboard_bp.route("/api/dashboard/monthly-trend")
@login_required
def api_monthly_trend():
    # Proxy monthly churn trend using tenure buckets (last 12 months of tenure).
    labels, values = [], []
    for m in range(12, 0, -1):
        lo, hi = (m - 1) * 1, m * 1
        cnt = (
            db.session.query(func.count(Customer.customer_id))
            .filter(Customer.churn == 1, Customer.tenure_months == m)
            .scalar()
        ) or 0
        labels.append(f"M{m}")
        values.append(int(cnt))
    return jsonify({"labels": labels, "values": values})


@dashboard_bp.route("/api/dashboard/province-stats")
@login_required
def api_province_stats():
    rows = (
        db.session.query(
            Province.province_name,
            Province.security_level,
            func.count(Customer.customer_id),
            func.sum(Customer.churn),
        )
        .join(Customer, Customer.province_id == Province.province_id)
        .group_by(Province.province_name, Province.security_level)
        .all()
    )
    data = []
    for name, sec, total, churned in rows:
        total = int(total or 0)
        churned = int(churned or 0)
        data.append({
            "province": name,
            "security_level": sec,
            "customers": total,
            "churned": churned,
            "churn_rate": round((churned / total * 100) if total else 0, 1),
        })
    data.sort(key=lambda x: x["churn_rate"], reverse=True)
    return jsonify(data)


@dashboard_bp.route("/api/dashboard/top-risk-customers")
@login_required
def api_top_risk_customers():
    # Top 10 customers at risk of churn (heuristic based on complaints, inactivity, etc.)
    from sqlalchemy import case
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
            "risk_score": round(float(risk), 1),
            "health_score": cust.health_score(),
            "health_status": cust.health_status(),
        })
    return jsonify(data)


@dashboard_bp.route("/api/dashboard/recent-activities")
@login_required
def api_recent_activities():
    # Simulated recent activities (since we don't have an activities table)
    # In production, this would query an activities table
    activities = [
        {"type": "churn", "message": "Customer #1423 churned", "time": "2 hours ago"},
        {"type": "add", "message": "New customer added in Kabul", "time": "4 hours ago"},
        {"type": "train", "message": "ML model retrained (AUC: 0.94)", "time": "6 hours ago"},
        {"type": "complaint", "message": "High complaint volume in Herat", "time": "8 hours ago"},
        {"type": "recharge", "message": "Bulk recharge campaign completed", "time": "12 hours ago"},
    ]
    return jsonify(activities)
