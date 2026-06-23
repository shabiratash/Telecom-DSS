"""Shared domain constants for the Afghanistan Telecom Churn Prediction and Retention System."""

# All 34 provinces of Afghanistan with an assigned baseline security level.
AFGHAN_PROVINCES = [
    ("Kabul", "High"),
    ("Herat", "Medium"),
    ("Kandahar", "Low"),
    ("Balkh", "Medium"),
    ("Nangarhar", "Low"),
    ("Kunduz", "Low"),
    ("Helmand", "Low"),
    ("Ghazni", "Low"),
    ("Baghlan", "Medium"),
    ("Badakhshan", "Medium"),
    ("Takhar", "Medium"),
    ("Faryab", "Low"),
    ("Jowzjan", "Medium"),
    ("Samangan", "Medium"),
    ("Sar-e Pol", "Medium"),
    ("Bamyan", "High"),
    ("Parwan", "Medium"),
    ("Kapisa", "Medium"),
    ("Panjshir", "High"),
    ("Logar", "Low"),
    ("Wardak", "Low"),
    ("Paktia", "Low"),
    ("Paktika", "Low"),
    ("Khost", "Low"),
    ("Ghor", "Medium"),
    ("Daikundi", "High"),
    ("Uruzgan", "Low"),
    ("Zabul", "Low"),
    ("Farah", "Low"),
    ("Nimroz", "Medium"),
    ("Badghis", "Low"),
    ("Laghman", "Low"),
    ("Kunar", "Low"),
    ("Nuristan", "Low"),
]

PROVINCE_NAMES = [p[0] for p in AFGHAN_PROVINCES]

GENDERS = ["Male", "Female"]
AREA_TYPES = ["Urban", "Rural"]
NETWORK_QUALITY = ["Poor", "Average", "Good", "Excellent"]
INTERNET_TYPES = ["2G", "3G", "4G", "5G", "Fiber"]
PAYMENT_METHODS = ["Cash", "Mobile Money", "Bank Transfer"]
TOWER_AVAILABILITY = ["Low", "Medium", "High"]
YES_NO = ["No", "Yes"]

# Feature columns (in canonical order) consumed by the ML pipeline.
NUMERIC_FEATURES = [
    "age",
    "call_drop_rate",
    "recharge_amount",
    "recharge_frequency",
    "tenure_months",
    "inactive_days",
    "complaint_count",
]

CATEGORICAL_FEATURES = [
    "gender",
    "province_name",
    "area_type",
    "network_quality",
    "internet_type",
    "payment_method",
    "tower_availability",
    "competitor_offer_exposure",
    "discount_usage",
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "churn"
