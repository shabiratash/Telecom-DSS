"""Province model. One province has many customers."""
from app.extensions import db


class Province(db.Model):
    __tablename__ = "provinces"

    province_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    province_name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    security_level = db.Column(db.String(20), nullable=False, default="Medium")

    customers = db.relationship(
        "Customer",
        back_populates="province",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "province_id": self.province_id,
            "province_name": self.province_name,
            "security_level": self.security_level,
            "customer_count": len(self.customers) if self.customers is not None else 0,
        }

    def __repr__(self):
        return f"<Province {self.province_name}>"
