"""
Logging service for the deployed system audit trail.

Additive and fully guarded: any failure here is swallowed so that it can
NEVER break prediction, recommendation, or any existing route. It does not
modify the ML prediction logic in any way -- it only persists a copy of the
result produced by the deployed system.

Tables are created lazily with checkfirst=True so the feature works even if
the SQL migration (sql/add_logging_tables.sql) has not been run yet.
"""
from flask import current_app

from app.extensions import db
from app.models import PredictionLog, RecommendationLog

_tables_ready = False


def _ensure_tables():
    """Create the two additive log tables if they do not yet exist.

    Uses checkfirst=True so existing tables are never touched/altered.
    """
    global _tables_ready
    if _tables_ready:
        return
    try:
        PredictionLog.__table__.create(bind=db.engine, checkfirst=True)
        RecommendationLog.__table__.create(bind=db.engine, checkfirst=True)
        _tables_ready = True
    except Exception as exc:  # pragma: no cover - defensive
        try:
            current_app.logger.warning("logging_service: ensure_tables failed: %s", exc)
        except Exception:
            pass


def log_prediction(result, customer_id=None, source="single", commit=True):
    """Persist a single prediction result. Returns the new PredictionLog id or None.

    `result` is the dict returned by ml.predictor.predict(); this function only
    reads from it, never mutates the prediction.
    """
    if not result:
        return None
    try:
        _ensure_tables()
        entry = PredictionLog(
            customer_id=customer_id,
            churn_probability=float(result.get("probability", 0) or 0),
            prediction=int(result.get("prediction", 0) or 0),
            prediction_label=result.get("prediction_label"),
            risk_level=result.get("risk_level"),
            health_score=result.get("health_score"),
            source=source,
        )
        db.session.add(entry)
        db.session.flush()  # assign id without full commit
        pred_id = entry.id

        # log associated recommendations (if present) tied to this prediction
        recs = result.get("recommendations") or []
        for r in recs:
            db.session.add(RecommendationLog(
                customer_id=customer_id,
                prediction_id=pred_id,
                title=r.get("title", "Recommendation")[:120],
                action=r.get("action"),
                severity=r.get("severity"),
                icon=r.get("icon"),
            ))

        if commit:
            db.session.commit()
        return pred_id
    except Exception as exc:  # pragma: no cover - defensive
        try:
            db.session.rollback()
            current_app.logger.warning("logging_service: log_prediction failed: %s", exc)
        except Exception:
            pass
        return None


def log_predictions_bulk(items, source="batch"):
    """Persist many predictions in a single commit.

    `items` is an iterable of (result_dict, customer_id) tuples.
    """
    count = 0
    try:
        _ensure_tables()
        for result, customer_id in items:
            if not result:
                continue
            entry = PredictionLog(
                customer_id=customer_id,
                churn_probability=float(result.get("probability", result.get("churn_probability", 0)) or 0),
                prediction=int(result.get("prediction", 0) or 0),
                prediction_label=result.get("prediction_label"),
                risk_level=result.get("risk_level"),
                health_score=result.get("health_score"),
                source=source,
            )
            db.session.add(entry)
            count += 1
        db.session.commit()
        return count
    except Exception as exc:  # pragma: no cover - defensive
        try:
            db.session.rollback()
            current_app.logger.warning("logging_service: log_predictions_bulk failed: %s", exc)
        except Exception:
            pass
        return 0
