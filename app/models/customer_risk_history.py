"""Customer risk history model for tracking risk changes over time."""
from app.extensions import db
from datetime import datetime


class CustomerRiskHistory(db.Model):
    __tablename__ = "customer_risk_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    risk_score = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    customer = db.relationship("Customer", backref="risk_history")

    def __repr__(self):
        return f"<CustomerRiskHistory customer_id={self.customer_id} risk={self.risk_score}>"
