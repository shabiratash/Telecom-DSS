"""Service layer package (additive, non-destructive)."""
from app.services.logging_service import log_prediction, log_predictions_bulk

__all__ = ["log_prediction", "log_predictions_bulk"]
