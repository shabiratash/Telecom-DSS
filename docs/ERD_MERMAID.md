# ERD Diagram - Mermaid Syntax

## Database Entity Relationship Diagram

```mermaid
erDiagram
    PROVINCES ||--o{ CUSTOMERS : "has many"
    CUSTOMERS ||--o{ CUSTOMER_RISK_HISTORY : "has many"
    CUSTOMERS ||--o{ MODEL_TRAINING_HISTORY : "trains on"

    PROVINCES {
        int province_id PK
        string province_name UK
        string security_level
    }

    CUSTOMERS {
        int customer_id PK
        int age
        string gender
        int province_id FK
        string area_type
        string network_quality
        string internet_type
        float call_drop_rate
        float recharge_amount
        int recharge_frequency
        string payment_method
        int tenure_months
        int inactive_days
        int complaint_count
        string tower_availability
        string competitor_offer_exposure
        string discount_usage
        tinyint churn
    }

    CUSTOMER_RISK_HISTORY {
        int id PK
        int customer_id FK
        float risk_score
        datetime recorded_at
    }

    MODEL_TRAINING_HISTORY {
        int id PK
        string model_name
        float accuracy
        float precision
        float recall
        float f1
        float roc_auc
        json confusion_matrix
        datetime trained_at
        int n_samples
        float churn_rate
    }
```

## Simplified ERD (Core Tables)

```mermaid
erDiagram
    PROVINCES ||--o{ CUSTOMERS : "contains"
    CUSTOMERS ||--o{ CUSTOMER_RISK_HISTORY : "tracks risk"

    PROVINCES {
        int province_id PK
        string province_name
        string security_level
    }

    CUSTOMERS {
        int customer_id PK
        int province_id FK
        int age
        string gender
        string area_type
        string network_quality
        float call_drop_rate
        float recharge_amount
        int recharge_frequency
        int tenure_months
        int inactive_days
        int complaint_count
        string competitor_offer_exposure
        tinyint churn
    }

    CUSTOMER_RISK_HISTORY {
        int id PK
        int customer_id FK
        float risk_score
        datetime recorded_at
    }
```

## Entity Relationship Details

### Relationships
- **PROVINCES → CUSTOMERS**: One-to-Many (One province has many customers)
- **CUSTOMERS → CUSTOMER_RISK_HISTORY**: One-to-Many (One customer has many risk history records)
- **CUSTOMERS → MODEL_TRAINING_HISTORY**: One-to-Many (Customers are used to train models)

### Foreign Keys
- `customers.province_id` → `provinces.province_id` (CASCADE DELETE)
- `customer_risk_history.customer_id` → `customers.customer_id` (CASCADE DELETE)

### Indexes
- `idx_customers_province` on `customers.province_id`
- `idx_customers_churn` on `customers.churn`
- `idx_risk_customer` on `customer_risk_history.customer_id`
- `idx_risk_recorded` on `customer_risk_history.recorded_at`
