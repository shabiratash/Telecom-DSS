# Database Review Report

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Database:** MySQL - telecom_churn_db
**Date:** June 22, 2026

---

## Database Overview

**Database Name:** `telecom_churn_db`
**Character Set:** utf8mb4
**Collation:** utf8mb4_unicode_ci
**Engine:** InnoDB

---

## Table Descriptions

### 1. provinces

**Purpose:** Stores Afghanistan's 34 provinces with security level classification

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `province_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for province |
| `province_name` | VARCHAR(100) | NOT NULL, UNIQUE | Province name (e.g., Kabul, Herat) |
| `security_level` | VARCHAR(20) | NOT NULL, DEFAULT 'Medium' | Security classification |

**Indexes:**
- PRIMARY KEY on `province_id`
- UNIQUE on `province_name`

**Relationships:**
- One-to-Many with `customers` table

---

### 2. customers

**Purpose:** Stores customer demographic, usage, and churn data

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `customer_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique customer identifier |
| `age` | INT | NOT NULL | Customer age |
| `gender` | VARCHAR(10) | NOT NULL | Customer gender |
| `province_id` | INT | NOT NULL, FOREIGN KEY | Reference to province |
| `area_type` | VARCHAR(20) | NOT NULL, DEFAULT 'Urban' | Urban/Rural classification |
| `network_quality` | VARCHAR(20) | NOT NULL, DEFAULT 'Good' | Network quality rating |
| `internet_type` | VARCHAR(20) | NOT NULL, DEFAULT '4G' | Internet connection type |
| `call_drop_rate` | FLOAT | NOT NULL, DEFAULT 0 | Call drop percentage |
| `recharge_amount` | FLOAT | NOT NULL, DEFAULT 0 | Average monthly recharge amount |
| `recharge_frequency` | INT | NOT NULL, DEFAULT 0 | Recharges per month |
| `payment_method` | VARCHAR(20) | NOT NULL, DEFAULT 'Cash' | Payment method |
| `tenure_months` | INT | NOT NULL, DEFAULT 0 | Customer tenure in months |
| `inactive_days` | INT | NOT NULL, DEFAULT 0 | Days since last activity |
| `complaint_count` | INT | NOT NULL, DEFAULT 0 | Number of complaints filed |
| `tower_availability` | VARCHAR(20) | NOT NULL, DEFAULT 'High' | Tower coverage availability |
| `competitor_offer_exposure` | VARCHAR(10) | NOT NULL, DEFAULT 'No' | Competitor offer exposure |
| `discount_usage` | VARCHAR(10) | NOT NULL, DEFAULT 'No' | Discount usage status |
| `churn` | TINYINT | NOT NULL, DEFAULT 0 | Churn status (0=No, 1=Yes) |

**Indexes:**
- PRIMARY KEY on `customer_id`
- INDEX `idx_customers_province` on `province_id`
- INDEX `idx_customers_churn` on `churn`

**Foreign Keys:**
- `fk_customer_province` → `provinces.province_id`
  - ON DELETE CASCADE
  - ON UPDATE CASCADE

**Relationships:**
- Many-to-One with `provinces` table
- One-to-Many with `customer_risk_history` table

---

### 3. customer_risk_history

**Purpose:** Tracks customer risk score changes over time for early warning system

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique history record identifier |
| `customer_id` | INT | NOT NULL, FOREIGN KEY | Reference to customer |
| `risk_score` | FLOAT | NOT NULL | Calculated risk score |
| `recorded_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of risk recording |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX `idx_risk_customer` on `customer_id`
- INDEX `idx_risk_recorded` on `recorded_at`

**Foreign Keys:**
- `fk_risk_customer` → `customers.customer_id`
  - ON DELETE CASCADE
  - ON UPDATE CASCADE

**Relationships:**
- Many-to-One with `customers` table

---

## Database Architecture

### Entity Relationships

```
provinces (1) ──< (N) customers (1) ──< (N) customer_risk_history
```

### Relationship Types

1. **provinces → customers**: One-to-Many
   - One province can have many customers
   - Each customer belongs to exactly one province
   - Cascade delete: Deleting a province deletes all its customers

2. **customers → customer_risk_history**: One-to-Many
   - One customer can have many risk history records
   - Each risk history record belongs to exactly one customer
   - Cascade delete: Deleting a customer deletes all risk history

---

## Constraint Verification

### Primary Keys
✅ All tables have proper primary keys:
- `provinces.province_id` (AUTO_INCREMENT)
- `customers.customer_id` (AUTO_INCREMENT)
- `customer_risk_history.id` (AUTO_INCREMENT)

### Foreign Keys
✅ All foreign keys properly defined:
- `customers.province_id` → `provinces.province_id`
- `customer_risk_history.customer_id` → `customers.customer_id`

### Referential Integrity
✅ CASCADE rules configured:
- ON DELETE CASCADE: Maintains referential integrity
- ON UPDATE CASCADE: Updates propagate to child records

### Unique Constraints
✅ Unique constraint on `provinces.province_name` prevents duplicate provinces

### NOT NULL Constraints
✅ All essential columns have NOT NULL constraints to prevent NULL data

### Default Values
✅ Appropriate defaults set for optional fields:
- `area_type`: 'Urban'
- `network_quality`: 'Good'
- `internet_type`: '4G'
- `call_drop_rate`: 0
- `recharge_amount`: 0
- `recharge_frequency`: 0
- `payment_method`: 'Cash'
- `tenure_months`: 0
- `inactive_days`: 0
- `complaint_count`: 0
- `tower_availability`: 'High'
- `competitor_offer_exposure`: 'No'
- `discount_usage`: 'No'
- `churn`: 0
- `security_level`: 'Medium'
- `recorded_at`: CURRENT_TIMESTAMP

---

## Index Analysis

### Performance Indexes

| Index | Table | Columns | Purpose |
|-------|-------|---------|---------|
| PRIMARY | provinces | province_id | Primary key lookup |
| UNIQUE | provinces | province_name | Province name uniqueness |
| PRIMARY | customers | customer_id | Primary key lookup |
| idx_customers_province | customers | province_id | Province-based queries |
| idx_customers_churn | customers | churn | Churn-based filtering |
| PRIMARY | customer_risk_history | id | Primary key lookup |
| idx_risk_customer | customer_risk_history | customer_id | Customer risk history lookup |
| idx_risk_recorded | customer_risk_history | recorded_at | Time-based queries |

### Index Recommendations

✅ **Current indexes are well-designed for:**
- Province-based analytics (idx_customers_province)
- Churn prediction queries (idx_customers_churn)
- Risk history time-series analysis (idx_risk_recorded)
- Customer-specific risk tracking (idx_risk_customer)

📝 **Potential additions (if needed):**
- Composite index on `customer_risk_history(customer_id, recorded_at)` for trend analysis
- Index on `customers.inactive_days` for early warning queries
- Index on `customers.complaint_count` for complaint-based analytics

---

## Data Integrity Assessment

### Referential Integrity
✅ **PASS** - All foreign key relationships properly defined with CASCADE rules

### Domain Integrity
✅ **PASS** - Appropriate data types and constraints for all columns

### Entity Integrity
✅ **PASS** - Primary keys properly defined on all tables

### Business Rule Integrity
✅ **PASS** - Default values align with business requirements

---

## Database Health Score

| Category | Score | Status |
|----------|-------|--------|
| Schema Design | 10/10 | ✅ Excellent |
| Relationships | 10/10 | ✅ Excellent |
| Indexing | 9/10 | ✅ Very Good |
| Constraints | 10/10 | ✅ Excellent |
| Normalization | 10/10 | ✅ Excellent |
| **Overall** | **9.8/10** | ✅ **Excellent** |

---

## Summary

The database schema is well-designed with:
- Proper normalization (3NF compliant)
- Appropriate foreign key relationships with CASCADE rules
- Strategic indexing for query performance
- Comprehensive constraints for data integrity
- Clear separation of concerns across tables

**No critical issues identified.** The database is production-ready for the thesis project.
