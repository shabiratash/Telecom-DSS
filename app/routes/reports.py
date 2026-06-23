"""Reports controller: CSV, Excel and PDF exports."""
import io
from datetime import datetime

import pandas as pd
from flask import Blueprint, send_file, flash, redirect, url_for, current_app
from sqlalchemy import func

from app.extensions import db
from app.models import Customer, Province
from app.routes.helpers import login_required
from app.ml import predictor

reports_bp = Blueprint("reports", __name__)


def _customers_dataframe():
    rows = (
        db.session.query(Customer, Province.province_name)
        .join(Province, Customer.province_id == Province.province_id)
        .order_by(Customer.customer_id)
        .all()
    )
    records = []
    for c, pname in rows:
        d = c.to_dict()
        d["province_name"] = pname
        records.append(d)
    return pd.DataFrame(records)


@reports_bp.route("/reports/csv")
@login_required
def export_csv():
    df = _customers_dataframe()
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    mem = io.BytesIO(buf.getvalue().encode("utf-8"))
    return send_file(mem, mimetype="text/csv", as_attachment=True,
                     download_name=f"customers_{datetime.now():%Y%m%d_%H%M}.csv")


@reports_bp.route("/reports/excel")
@login_required
def export_excel():
    df = _customers_dataframe()
    # analytics summary sheet
    total = len(df)
    churned = int(df["churn"].sum()) if total else 0
    summary = pd.DataFrame({
        "Metric": ["Total Customers", "Churned", "Active", "Churn Rate %",
                   "Avg Recharge", "Avg Complaints"],
        "Value": [
            total, churned, total - churned,
            round((churned / total * 100) if total else 0, 2),
            round(df["recharge_amount"].mean() if total else 0, 2),
            round(df["complaint_count"].mean() if total else 0, 2),
        ],
    })
    prov = (df.groupby("province_name")
            .agg(customers=("customer_id", "count"), churned=("churn", "sum"))
            .reset_index()) if total else pd.DataFrame()

    mem = io.BytesIO()
    with pd.ExcelWriter(mem, engine="xlsxwriter") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        if not prov.empty:
            prov.to_excel(writer, sheet_name="Provinces", index=False)
        df.to_excel(writer, sheet_name="Customers", index=False)
    mem.seek(0)
    return send_file(
        mem,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"telecom_report_{datetime.now():%Y%m%d_%H%M}.xlsx",
    )


@reports_bp.route("/reports/pdf")
@login_required
def export_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except Exception as exc:  # pragma: no cover
        flash(f"PDF library unavailable: {exc}", "danger")
        return redirect(url_for("dashboard.index"))

    total = db.session.query(func.count(Customer.customer_id)).scalar() or 0
    churned = db.session.query(func.count(Customer.customer_id)).filter(Customer.churn == 1).scalar() or 0
    avg_recharge = db.session.query(func.avg(Customer.recharge_amount)).scalar() or 0
    avg_complaints = db.session.query(func.avg(Customer.complaint_count)).scalar() or 0

    mem = io.BytesIO()
    doc = SimpleDocTemplate(mem, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("t", parent=styles["Title"], textColor=colors.HexColor("#6d5dfc"))
    elements = [
        Paragraph("Afghanistan Telecom Churn Prediction and Retention Report", title_style),
        Paragraph(f"Generated: {datetime.now():%Y-%m-%d %H:%M}", styles["Normal"]),
        Spacer(1, 16),
    ]

    summary_data = [
        ["Metric", "Value"],
        ["Total Customers", f"{total:,}"],
        ["Churned Customers", f"{churned:,}"],
        ["Active Customers", f"{total - churned:,}"],
        ["Churn Rate", f"{(churned / total * 100) if total else 0:.2f}%"],
        ["Average Recharge", f"{float(avg_recharge):.2f}"],
        ["Average Complaints", f"{float(avg_complaints):.2f}"],
    ]
    t = Table(summary_data, colWidths=[8 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a2350")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#eef0ff")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elements += [Paragraph("Analytics Summary", styles["Heading2"]), t, Spacer(1, 16)]

    if predictor.model_available():
        meta = predictor.get_metadata()
        m = meta["metrics"][meta["best_model"]]
        model_data = [["Best Model", meta["best_model"]],
                      ["Accuracy", m["accuracy"]], ["Precision", m["precision"]],
                      ["Recall", m["recall"]], ["F1 Score", m["f1"]], ["ROC-AUC", m["roc_auc"]]]
        mt = Table(model_data, colWidths=[8 * cm, 6 * cm])
        mt.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef0ff")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements += [Paragraph("Model Performance", styles["Heading2"]), mt]

    doc.build(elements)
    mem.seek(0)
    return send_file(mem, mimetype="application/pdf", as_attachment=True,
                     download_name=f"telecom_report_{datetime.now():%Y%m%d_%H%M}.pdf")
