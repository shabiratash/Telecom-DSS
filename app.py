"""
Afghanistan Telecom Churn Prediction and Retention System
Flask application factory (MVC architecture).
"""
import os
from flask import Flask, redirect, url_for, session

from app.config import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ensure runtime directories exist
    for d in (config_class.ML_MODEL_DIR, config_class.DATASET_DIR, config_class.UPLOAD_DIR):
        os.makedirs(d, exist_ok=True)

    db.init_app(app)

    # models must be imported so SQLAlchemy registers the tables
    from app.models import Province, Customer, ModelTrainingHistory  # noqa: F401

    # blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.customer import customer_bp
    from app.routes.prediction import prediction_bp
    from app.routes.analytics import analytics_bp
    from app.routes.reports import reports_bp
    from app.routes.ml_center import ml_center_bp
    from app.routes.whatif_simulator import whatif_bp
    from app.routes.early_warning import early_warning_bp
    from app.routes.financial_impact import financial_bp
    from app.routes.customer_portal import customer_portal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(ml_center_bp)
    app.register_blueprint(whatif_bp)
    app.register_blueprint(early_warning_bp)
    app.register_blueprint(financial_bp)
    app.register_blueprint(customer_portal_bp)

    @app.route("/")
    def index():
        if session.get("logged_in"):
            role = session.get("role", "admin")
            if role == "customer":
                return redirect(url_for("customer_portal.home"))
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    @app.context_processor
    def inject_globals():
        return {"app_name": "Afghanistan Telecom Churn Prediction and Retention System", "current_user": session.get("username")}

    return app
