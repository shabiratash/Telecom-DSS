"""Model Training History model. Tracks ML model training sessions."""
from datetime import datetime
from app.extensions import db


class ModelTrainingHistory(db.Model):
    __tablename__ = "model_training_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision_score = db.Column(db.Float, nullable=False)
    recall_score = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    training_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_best_model = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "accuracy": self.accuracy,
            "precision_score": self.precision_score,
            "recall_score": self.recall_score,
            "f1_score": self.f1_score,
            "training_date": self.training_date.isoformat() if self.training_date else None,
            "is_best_model": self.is_best_model,
        }

    def __repr__(self):
        return f"<ModelTrainingHistory {self.model_name} acc={self.accuracy}>"
