# Database Schema — `telecom_churn_db`

## Table: `provinces`
One province has many customers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `province_id` | INT | PK, AUTO_INCREMENT | Unique province id |
| `province_name` | VARCHAR(100) | NOT NULL, UNIQUE | Province name (34 total) |
| `security_level` | VARCHAR(20) | NOT NULL, default `Medium` | High / Medium / Low |

## Table: `customers`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `customer_id` | INT | PK, AUTO_INCREMENT | Unique customer id |
| `age` | INT | NOT NULL | Customer age (18-70) |
| `gender` | VARCHAR(10) | NOT NULL | Male / Female |
| `province_id` | INT | FK → provinces.province_id, ON DELETE CASCADE | Province |
| `area_type` | VARCHAR(20) | NOT NULL | Urban / Rural |
| `network_quality` | VARCHAR(20) | NOT NULL | Poor / Average / Good / Excellent |
| `internet_type` | VARCHAR(20) | NOT NULL | 2G / 3G / 4G / 5G / Fiber |
| `call_drop_rate` | FLOAT | NOT NULL | Dropped call % (0-20) |
| `recharge_amount` | FLOAT | NOT NULL | Avg recharge (AFN, 50-5000) |
| `recharge_frequency` | INT | NOT NULL | Top-ups per month (1-30) |
| `payment_method` | VARCHAR(20) | NOT NULL | Cash / Mobile Money / Bank Transfer |
| `tenure_months` | INT | NOT NULL | Months as customer (1-120) |
| `inactive_days` | INT | NOT NULL | Days since last activity (0-90) |
| `complaint_count` | INT | NOT NULL | Lifetime complaints (0-20) |
| `tower_availability` | VARCHAR(20) | NOT NULL | Low / Medium / High |
| `competitor_offer_exposure` | VARCHAR(10) | NOT NULL | Yes / No |
| `discount_usage` | VARCHAR(10) | NOT NULL | Yes / No |
| `churn` | TINYINT | NOT NULL, default 0 | 1 = churned, 0 = active |

### Indexes
- `idx_customers_province` on `province_id`
- `idx_customers_churn` on `churn`

### Relationship
`provinces (1) ──< customers (N)` — a one-to-many relationship enforced by the
`fk_customer_province` foreign key with cascading delete.

### Enumerated Values

#### Area Type
- `Urban` - City/metropolitan areas
- `Rural` - Village/rural areas

#### Network Quality
- `Poor` - Frequent drops, low signal
- `Average` - Moderate signal quality
- `Good` - Reliable connection
- `Excellent` - Premium signal quality

#### Internet Type
- `2G` - Basic GPRS/EDGE
- `3G` - HSPA/HSPA+
- `4G` - LTE
- `5G` - Next-generation mobile
- `Fiber` - Fixed broadband

#### Payment Method
- `Cash` - Physical cash payments
- `Mobile Money` - Digital wallet (e.g., Etisalat, Roshan)
- `Bank Transfer` - Direct bank transfer

#### Tower Availability
- `Low` - Sparse tower coverage
- `Medium` - Adequate coverage
- `High` - Dense tower network
