# Data Dictionary — `telecom_churn_db`

## Overview
This data dictionary provides detailed descriptions of all tables, columns, relationships, and business rules for the Afghanistan Telecom Churn Prediction and Retention System database.

---

## Table: `provinces`

### Description
Reference table containing all 34 provinces of Afghanistan with their security risk levels. This table is used to categorize customers by geographic region and assess regional churn patterns.

### Columns

| Column | Type | Length | Nullable | Default | Description |
|--------|------|--------|----------|---------|-------------|
| `province_id` | INT | - | NO | AUTO_INCREMENT | Primary key. Unique identifier for each province. |
| `province_name` | VARCHAR | 100 | NO | - | Name of the province in English. Must be unique. |
| `security_level` | VARCHAR | 20 | NO | 'Medium' | Security risk level: 'High', 'Medium', or 'Low'. Used for risk assessment. |

### Constraints
- **Primary Key**: `province_id`
- **Unique**: `province_name`
- **Default**: `security_level = 'Medium'`

### Business Rules
- All 34 provinces of Afghanistan must be present.
- Security levels are based on regional stability assessments.
- Deleting a province cascades to delete all associated customers.

### Sample Data
| province_id | province_name | security_level |
|-------------|---------------|----------------|
| 1 | Kabul | High |
| 2 | Herat | Medium |
| 3 | Kandahar | Low |

---

## Table: `customers`

### Description
Core table containing customer records with demographic, usage, and behavioral features used for churn prediction. Each customer belongs to exactly one province.

### Columns

| Column | Type | Length | Nullable | Default | Description |
|--------|------|--------|----------|---------|-------------|
| `customer_id` | INT | - | NO | AUTO_INCREMENT | Primary key. Unique identifier for each customer. |
| `age` | INT | - | NO | - | Customer age in years. Range: 18-70. |
| `gender` | VARCHAR | 10 | NO | - | Customer gender: 'Male' or 'Female'. |
| `province_id` | INT | - | NO | - | Foreign key to provinces table. Indicates customer's province. |
| `area_type` | VARCHAR | 20 | NO | 'Urban' | Geographic area type: 'Urban' or 'Rural'. |
| `network_quality` | VARCHAR | 20 | NO | 'Good' | Self-reported network quality: 'Poor', 'Average', 'Good', or 'Excellent'. |
| `internet_type` | VARCHAR | 20 | NO | '4G' | Internet connection type: '2G', '3G', '4G', '5G', or 'Fiber'. |
| `call_drop_rate` | FLOAT | - | NO | 0 | Percentage of dropped calls. Range: 0-20. |
| `recharge_amount` | FLOAT | - | NO | 0 | Average monthly recharge amount in AFN. Range: 50-5000. |
| `recharge_frequency` | INT | - | NO | 0 | Number of recharges per month. Range: 1-30. |
| `payment_method` | VARCHAR | 20 | NO | 'Cash' | Preferred payment method: 'Cash', 'Mobile Money', or 'Bank Transfer'. |
| `tenure_months` | INT | - | NO | 0 | Total months as a customer. Range: 1-120. |
| `inactive_days` | INT | - | NO | 0 | Days since last activity/recharge. Range: 0-90. |
| `complaint_count` | INT | - | NO | 0 | Total number of complaints filed. Range: 0-20. |
| `tower_availability` | VARCHAR | 20 | NO | 'High' | Tower coverage density: 'Low', 'Medium', or 'High'. |
| `competitor_offer_exposure` | VARCHAR | 10 | NO | 'No' | Whether customer has seen competitor offers: 'Yes' or 'No'. |
| `discount_usage` | VARCHAR | 10 | NO | 'No' | Whether customer uses discounts: 'Yes' or 'No'. |
| `churn` | TINYINT | - | NO | 0 | Churn status: 1 = churned, 0 = active. |

### Constraints
- **Primary Key**: `customer_id`
- **Foreign Key**: `province_id` → `provinces.province_id` (ON DELETE CASCADE)
- **Indexes**: 
  - `idx_customers_province` on `province_id`
  - `idx_customers_churn` on `churn`

### Business Rules

#### Age
- Minimum age: 18 years
- Maximum age: 70 years
- Used in risk assessment (younger customers may have higher churn)

#### Gender
- Binary classification: Male or Female
- Distribution: ~60% Male, ~40% Female (reflects Afghanistan demographics)

#### Province
- Must reference a valid province_id
- Province security level affects churn risk
- Larger provinces (Kabul, Herat, Kandahar) have more customers

#### Area Type
- Urban: City/metropolitan areas with better infrastructure
- Rural: Village/rural areas with limited infrastructure
- Rural customers may have higher churn due to network issues

#### Network Quality
- Poor: Frequent drops, low signal strength
- Average: Moderate signal quality
- Good: Reliable connection
- Excellent: Premium signal quality
- Poor network quality is a strong churn predictor

#### Internet Type
- 2G: Basic GPRS/EDGE (slow, legacy)
- 3G: HSPA/HSPA+ (moderate speed)
- 4G: LTE (high speed, most common)
- 5G: Next-generation (premium, limited coverage)
- Fiber: Fixed broadband (highest quality)
- Faster internet types correlate with lower churn

#### Call Drop Rate
- Percentage of dropped calls (0-20%)
- Higher rates indicate poor network quality
- Strong predictor of churn dissatisfaction

#### Recharge Amount
- Average monthly recharge in Afghan Afghani (AFN)
- Range: 50-5000 AFN
- Higher spend typically indicates lower churn risk

#### Recharge Frequency
- Number of top-ups per month (1-30)
- Low frequency (<3) indicates engagement issues
- High frequency indicates active usage

#### Payment Method
- Cash: Physical payments at retail outlets
- Mobile Money: Digital wallets (Etisalat, Roshan, etc.)
- Bank Transfer: Direct bank transfers
- Mobile Money users may have higher engagement

#### Tenure Months
- Total months as a customer (1-120)
- Longer tenure indicates loyalty
- New customers (<6 months) have higher churn risk

#### Inactive Days
- Days since last activity or recharge (0-90)
- High inactivity (>45 days) is a strong churn indicator
- Active customers (<10 days) are low risk

#### Complaint Count
- Total lifetime complaints (0-20)
- High complaints (>5) indicate dissatisfaction
- Zero complaints indicate satisfied customers

#### Tower Availability
- Low: Sparse tower coverage, poor signal
- Medium: Adequate coverage
- High: Dense tower network, excellent signal
- Low availability correlates with higher churn

#### Competitor Offer Exposure
- Yes: Customer has seen competitor promotions
- No: No known competitor exposure
- Exposure increases churn risk

#### Discount Usage
- Yes: Customer uses discounts/promotions
- No: Customer does not use discounts
- Discount users may have lower churn due to perceived value

#### Churn
- 1: Customer has churned (left the service)
- 0: Customer is active
- Target variable for ML prediction
- Target distribution: ~30% churned, ~70% active

### Relationships
- **Many-to-One**: Many customers belong to one province
- **Cascade Delete**: Deleting a province deletes all its customers

### Sample Data
| customer_id | age | gender | province_id | area_type | network_quality | internet_type | call_drop_rate | recharge_amount | recharge_frequency | payment_method | tenure_months | inactive_days | complaint_count | tower_availability | competitor_offer_exposure | discount_usage | churn |
|-------------|-----|--------|-------------|-----------|-----------------|---------------|----------------|-----------------|---------------------|----------------|---------------|---------------|-----------------|-------------------|--------------------------|----------------|-------|
| 1 | 28 | Male | 1 | Urban | Poor | 3G | 12.5 | 150.00 | 2 | Cash | 4 | 45 | 5 | Low | Yes | No | 1 |
| 2 | 35 | Female | 2 | Urban | Good | 4G | 3.2 | 500.00 | 8 | Mobile Money | 24 | 5 | 1 | High | No | Yes | 0 |

---

## Indexes

### Performance Indexes
| Index Name | Table | Columns | Type | Purpose |
|------------|-------|---------|------|---------|
| `idx_customers_province` | customers | province_id | B-Tree | Speed up province-based queries |
| `idx_customers_churn` | customers | churn | B-Tree | Speed up churn status filtering |

---

## Foreign Keys

| FK Name | Child Table | Child Column | Parent Table | Parent Column | On Delete | On Update |
|---------|-------------|--------------|--------------|----------------|-----------|-----------|
| `fk_customer_province` | customers | province_id | provinces | province_id | CASCADE | CASCADE |

---

## Data Integrity Rules

1. **Province Validation**: All customers must have a valid province_id
2. **Age Range**: Customer age must be between 18 and 70
3. **Churn Binary**: churn field must be 0 or 1
4. **Positive Values**: Numeric fields (recharge_amount, tenure_months, etc.) must be non-negative
5. **Cascading Deletes**: Deleting a province removes all associated customers

---

## ML Feature Mapping

The `customers` table provides 15 features for machine learning:

### Numeric Features (7)
1. `age` - Customer age
2. `call_drop_rate` - Network quality indicator
3. `recharge_amount` - Spend level
4. `recharge_frequency` - Engagement level
5. `tenure_months` - Loyalty indicator
6. `inactive_days` - Activity level
7. `complaint_count` - Satisfaction indicator

### Categorical Features (9)
1. `gender` - Demographic
2. `province_name` (via FK) - Geographic
3. `area_type` - Geographic density
4. `network_quality` - Service quality
5. `internet_type` - Technology tier
6. `payment_method` - Payment preference
7. `tower_availability` - Infrastructure
8. `competitor_offer_exposure` - Competitive pressure
9. `discount_usage` - Promotional engagement

### Target Variable
- `churn` - Binary classification target

---

## Security Considerations

1. **Access Control**: Database access restricted to application layer
2. **Data Masking**: No PII beyond age and gender
3. **Audit Trail**: Application logs all data modifications
4. **Backup Strategy**: Regular MySQL dumps recommended

---

## Maintenance Notes

1. **Province Updates**: Add new provinces only if Afghanistan administrative divisions change
2. **Data Archival**: Consider archiving churned customers older than 2 years
3. **Index Maintenance**: Rebuild indexes after bulk data operations
4. **Statistics Updates**: Run `ANALYZE TABLE` after major data changes
