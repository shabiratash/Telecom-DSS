"""Models package."""
from app.models.province import Province
from app.models.customer import Customer
from app.models.training_history import ModelTrainingHistory
from app.models.customer_risk_history import CustomerRiskHistory
from app.models.prediction_log import PredictionLog
from app.models.recommendation_log import RecommendationLog

__all__ = [
    "Province", "Customer", "ModelTrainingHistory", "CustomerRiskHistory",
    "PredictionLog", "RecommendationLog",
]
