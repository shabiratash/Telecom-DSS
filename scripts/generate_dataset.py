"""
Generate a realistic Afghanistan telecom customer dataset (15,000 records)
across all 34 provinces and export to dataset/telecom_dataset.csv.

Churn is generated intelligently based on specific risk factors:
- High probability: inactive_days > 45, complaint_count > 5, network_quality = Poor,
  recharge_frequency < 3, call_drop_rate > 10
- Low probability: inactive_days < 10, complaint_count < 2, network_quality Good/Excellent,
  tenure_months > 24
Target: 30% churn, 70% active
"""
import os
import numpy as np
import pandas as pd

from app.config import Config
from app.constants import (
    AFGHAN_PROVINCES,
    GENDERS,
    AREA_TYPES,
    NETWORK_QUALITY,
    INTERNET_TYPES,
    PAYMENT_METHODS,
    TOWER_AVAILABILITY,
    YES_NO,
)

RNG = np.random.default_rng(42)
N = 15000

SECURITY_RISK = {"High": -0.4, "Medium": 0.0, "Low": 0.5}
NETWORK_RISK = {"Excellent": -0.9, "Good": -0.4, "Average": 0.3, "Poor": 1.1}
INTERNET_RISK = {"Fiber": -0.9, "5G": -0.7, "4G": -0.5, "3G": -0.1, "2G": 0.4}
TOWER_RISK = {"High": -0.5, "Medium": 0.1, "Low": 0.8}
AREA_RISK = {"Urban": -0.3, "Rural": 0.5}


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def generate():
    provinces = [p[0] for p in AFGHAN_PROVINCES]
    sec_levels = {name: lvl for name, lvl in AFGHAN_PROVINCES}

    # Province popularity weights (Kabul, Herat, Kandahar, Balkh, Nangarhar larger)
    weights = np.ones(len(provinces))
    big = {"Kabul": 6.0, "Herat": 3.0, "Kandahar": 2.8, "Balkh": 2.5, "Nangarhar": 2.3,
           "Kunduz": 1.8, "Helmand": 1.6, "Ghazni": 1.5}
    for i, p in enumerate(provinces):
        weights[i] = big.get(p, 1.0)
    weights = weights / weights.sum()

    province_choice = RNG.choice(provinces, size=N, p=weights)

    age = RNG.integers(18, 71, size=N)
    gender = RNG.choice(GENDERS, size=N, p=[0.60, 0.40])
    area_type = RNG.choice(AREA_TYPES, size=N, p=[0.60, 0.40])
    network_quality = RNG.choice(NETWORK_QUALITY, size=N, p=[0.18, 0.34, 0.34, 0.14])
    internet_type = RNG.choice(INTERNET_TYPES, size=N, p=[0.08, 0.15, 0.35, 0.27, 0.15])
    payment_method = RNG.choice(PAYMENT_METHODS, size=N, p=[0.60, 0.25, 0.15])
    tower_availability = RNG.choice(TOWER_AVAILABILITY, size=N, p=[0.25, 0.40, 0.35])
    competitor_offer_exposure = RNG.choice(YES_NO, size=N, p=[0.55, 0.45])
    discount_usage = RNG.choice(YES_NO, size=N, p=[0.6, 0.4])

    call_drop_rate = np.clip(RNG.normal(8, 5, size=N), 0, 20).round(2)
    recharge_amount = np.clip(RNG.gamma(1.5, 400, size=N), 50, 5000).round(2)
    recharge_frequency = np.clip(RNG.poisson(12, size=N), 1, 30).astype(int)
    tenure_months = np.clip(RNG.gamma(2.0, 14, size=N), 1, 120).astype(int)
    inactive_days = np.clip(RNG.gamma(1.6, 12, size=N), 0, 90).astype(int)
    complaint_count = np.clip(RNG.poisson(3.5, size=N), 0, 20).astype(int)

    # ---- intelligent churn generation based on rules ----
    risk = np.zeros(N)
    
    # High probability factors
    risk += (inactive_days > 45).astype(float) * 1.5
    risk += (complaint_count > 5).astype(float) * 1.2
    risk += (network_quality == "Poor").astype(float) * 1.0
    risk += (recharge_frequency < 3).astype(float) * 0.8
    risk += (call_drop_rate > 10).astype(float) * 0.7
    
    # Low probability factors (negative risk)
    risk -= (inactive_days < 10).astype(float) * 1.0
    risk -= (complaint_count < 2).astype(float) * 0.8
    risk -= ((network_quality == "Good") | (network_quality == "Excellent")).astype(float) * 0.6
    risk -= (tenure_months > 24).astype(float) * 0.5
    
    # Additional factors
    risk += (competitor_offer_exposure == "Yes").astype(float) * 0.4
    risk -= (discount_usage == "Yes").astype(float) * 0.3
    risk += RNG.normal(0, 0.3, size=N)  # noise
    
    # Adjust threshold to achieve ~30% churn rate
    prob = _sigmoid(risk - 0.7)
    churn = (RNG.random(N) < prob).astype(int)

    df = pd.DataFrame({
        "age": age,
        "gender": gender,
        "province_name": province_choice,
        "area_type": area_type,
        "network_quality": network_quality,
        "internet_type": internet_type,
        "call_drop_rate": call_drop_rate,
        "recharge_amount": recharge_amount,
        "recharge_frequency": recharge_frequency,
        "payment_method": payment_method,
        "tenure_months": tenure_months,
        "inactive_days": inactive_days,
        "complaint_count": complaint_count,
        "tower_availability": tower_availability,
        "competitor_offer_exposure": competitor_offer_exposure,
        "discount_usage": discount_usage,
        "churn": churn,
    })
    return df


def main():
    os.makedirs(Config.DATASET_DIR, exist_ok=True)
    df = generate()
    df.to_csv(Config.DATASET_PATH, index=False)
    print(f"Generated {len(df)} records -> {Config.DATASET_PATH}")
    print(f"Churn rate: {df['churn'].mean():.3f}")


if __name__ == "__main__":
    main()
