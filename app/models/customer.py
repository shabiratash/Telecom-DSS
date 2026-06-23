"""Customer model. Many customers belong to one province."""
from app.extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    province_id = db.Column(
        db.Integer,
        db.ForeignKey("provinces.province_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    area_type = db.Column(db.String(20), nullable=False, default="Urban")
    network_quality = db.Column(db.String(20), nullable=False, default="Good")
    internet_type = db.Column(db.String(20), nullable=False, default="4G")
    call_drop_rate = db.Column(db.Float, nullable=False, default=0.0)
    recharge_amount = db.Column(db.Float, nullable=False, default=0.0)
    recharge_frequency = db.Column(db.Integer, nullable=False, default=0)
    payment_method = db.Column(db.String(20), nullable=False, default="Cash")
    tenure_months = db.Column(db.Integer, nullable=False, default=0)
    inactive_days = db.Column(db.Integer, nullable=False, default=0)
    complaint_count = db.Column(db.Integer, nullable=False, default=0)
    tower_availability = db.Column(db.String(20), nullable=False, default="High")
    competitor_offer_exposure = db.Column(db.String(10), nullable=False, default="No")
    discount_usage = db.Column(db.String(10), nullable=False, default="No")
    churn = db.Column(db.Integer, nullable=False, default=0, index=True)

    province = db.relationship("Province", back_populates="customers")

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "age": self.age,
            "gender": self.gender,
            "province_id": self.province_id,
            "province_name": self.province.province_name if self.province else None,
            "area_type": self.area_type,
            "network_quality": self.network_quality,
            "internet_type": self.internet_type,
            "call_drop_rate": self.call_drop_rate,
            "recharge_amount": self.recharge_amount,
            "recharge_frequency": self.recharge_frequency,
            "payment_method": self.payment_method,
            "tenure_months": self.tenure_months,
            "inactive_days": self.inactive_days,
            "complaint_count": self.complaint_count,
            "tower_availability": self.tower_availability,
            "competitor_offer_exposure": self.competitor_offer_exposure,
            "discount_usage": self.discount_usage,
            "churn": self.churn,
        }

    def feature_dict(self):
        """Return the raw feature set used by the ML pipeline."""
        return {
            "age": self.age,
            "gender": self.gender,
            "province_name": self.province.province_name if self.province else "Unknown",
            "area_type": self.area_type,
            "network_quality": self.network_quality,
            "internet_type": self.internet_type,
            "call_drop_rate": self.call_drop_rate,
            "recharge_amount": self.recharge_amount,
            "recharge_frequency": self.recharge_frequency,
            "payment_method": self.payment_method,
            "tenure_months": self.tenure_months,
            "inactive_days": self.inactive_days,
            "complaint_count": self.complaint_count,
            "tower_availability": self.tower_availability,
            "competitor_offer_exposure": self.competitor_offer_exposure,
            "discount_usage": self.discount_usage,
        }

    def health_score(self):
        """Calculate customer health score (0-100) based on key metrics."""
        score = 100.0
        
        # Complaint count penalty (max -30)
        complaints = self.complaint_count or 0
        if complaints > 0:
            score -= min(complaints * 3, 30)
        
        # Inactive days penalty (max -25)
        inactive = self.inactive_days or 0
        if inactive > 0:
            score -= min(inactive * 0.5, 25)
        
        # Network quality penalty
        network_scores = {"Excellent": 0, "Good": -5, "Average": -15, "Poor": -25}
        score += network_scores.get(self.network_quality, -5)
        
        # Recharge frequency bonus/penalty
        rfreq = self.recharge_frequency or 0
        if rfreq >= 8:
            score += 10
        elif rfreq >= 5:
            score += 5
        elif rfreq <= 2:
            score -= 10
        
        # Call drop rate penalty (max -15)
        drop = self.call_drop_rate or 0
        if drop > 0:
            score -= min(drop * 0.6, 15)
        
        # Competitor exposure penalty
        if self.competitor_offer_exposure == "Yes":
            score -= 10
        
        # Discount usage bonus
        if self.discount_usage == "Yes":
            score += 5
        
        # Clamp to 0-100
        return max(0, min(100, int(score)))

    def health_status(self):
        """Get health status category based on health score."""
        score = self.health_score()
        if score <= 30:
            return "Critical"
        elif score <= 60:
            return "Warning"
        elif score <= 80:
            return "Good"
        else:
            return "Excellent"

    def __repr__(self):
        return f"<Customer #{self.customer_id} churn={self.churn}>"
