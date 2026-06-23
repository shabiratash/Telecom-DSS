"""
Seed the MySQL database (telecom_churn_db):
  1. create tables
  2. insert all 34 provinces
  3. bulk-load customers from dataset/telecom_dataset.csv

Run AFTER generate_dataset.py. Requires a running MySQL server.
"""
import os
import pandas as pd

from app.config import Config
from app.constants import AFGHAN_PROVINCES


def seed(batch_size=2000):
    # Imported here so the Flask app/context is created lazily.
    from app import create_app
    from app.extensions import db
    from app.models import Province, Customer

    app = create_app()
    with app.app_context():
        db.create_all()

        # ---- provinces ----
        existing = {p.province_name: p for p in Province.query.all()}
        name_to_id = {}
        for name, level in AFGHAN_PROVINCES:
            if name in existing:
                existing[name].security_level = level
                name_to_id[name] = existing[name].province_id
            else:
                p = Province(province_name=name, security_level=level)
                db.session.add(p)
                db.session.flush()
                name_to_id[name] = p.province_id
        db.session.commit()
        print(f"Seeded {len(name_to_id)} provinces.")

        # ---- customers ----
        if Customer.query.count() > 0:
            print("Customers already present; skipping customer load.")
            return

        if not os.path.exists(Config.DATASET_PATH):
            print("Dataset CSV not found; run generate_dataset.py to load customers.")
            return

        df = pd.read_csv(Config.DATASET_PATH)
        records = []
        for _, r in df.iterrows():
            pid = name_to_id.get(r["province_name"])
            if pid is None:
                continue
            records.append(Customer(
                age=int(r["age"]),
                gender=str(r["gender"]),
                province_id=pid,
                area_type=str(r["area_type"]),
                network_quality=str(r["network_quality"]),
                internet_type=str(r["internet_type"]),
                call_drop_rate=float(r["call_drop_rate"]),
                recharge_amount=float(r["recharge_amount"]),
                recharge_frequency=int(r["recharge_frequency"]),
                payment_method=str(r["payment_method"]),
                tenure_months=int(r["tenure_months"]),
                inactive_days=int(r["inactive_days"]),
                complaint_count=int(r["complaint_count"]),
                tower_availability=str(r["tower_availability"]),
                competitor_offer_exposure=str(r["competitor_offer_exposure"]),
                discount_usage=str(r["discount_usage"]),
                churn=int(r["churn"]),
            ))
            if len(records) >= batch_size:
                db.session.bulk_save_objects(records)
                db.session.commit()
                records = []
        if records:
            db.session.bulk_save_objects(records)
            db.session.commit()
        print(f"Seeded {Customer.query.count()} customers.")


if __name__ == "__main__":
    seed()
