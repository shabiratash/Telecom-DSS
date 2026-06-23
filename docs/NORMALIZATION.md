# Database Normalization Analysis

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Database:** MySQL - telecom_churn_db
**Date:** June 22, 2026

---

## Normalization Overview

The database schema follows the principles of database normalization to eliminate redundancy and ensure data integrity. This document analyzes the schema against First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF).

---

## First Normal Form (1NF)

### Definition
A table is in 1NF if:
1. All columns contain atomic (indivisible) values
2. Each record is unique
3. There are no repeating groups

### Analysis

#### provinces Table
✅ **1NF Compliant**
- All columns contain atomic values
- `province_id` is the primary key ensuring uniqueness
- No repeating groups

#### customers Table
✅ **1NF Compliant**
- All columns contain atomic values (no arrays, lists, or nested structures)
- `customer_id` is the primary key ensuring uniqueness
- No repeating groups
- Each attribute represents a single piece of information

#### customer_risk_history Table
✅ **1NF Compliant**
- All columns contain atomic values
- `id` is the primary key ensuring uniqueness
- No repeating groups
- Each record represents a single risk measurement

### 1NF Conclusion
**Status:** ✅ **PASS**

All tables satisfy First Normal Form requirements. All data is atomic, and each table has a unique primary key.

---

## Second Normal Form (2NF)

### Definition
A table is in 2NF if:
1. It is in 1NF
2. All non-key attributes are fully functionally dependent on the entire primary key
3. No partial dependencies exist (for composite primary keys)

### Analysis

#### provinces Table
✅ **2NF Compliant**
- Primary key: `province_id` (single column)
- All non-key attributes (`province_name`, `security_level`) are fully dependent on `province_id`
- No partial dependencies possible with single-column primary key

#### customers Table
✅ **2NF Compliant**
- Primary key: `customer_id` (single column)
- All non-key attributes are fully dependent on `customer_id`
- No partial dependencies possible with single-column primary key
- Foreign key `province_id` is dependent on `customer_id` (each customer belongs to one province)

#### customer_risk_history Table
✅ **2NF Compliant**
- Primary key: `id` (single column)
- All non-key attributes (`customer_id`, `risk_score`, `recorded_at`) are fully dependent on `id`
- No partial dependencies possible with single-column primary key

### 2NF Conclusion
**Status:** ✅ **PASS**

All tables satisfy Second Normal Form requirements. All tables have single-column primary keys, eliminating the possibility of partial dependencies.

---

## Third Normal Form (3NF)

### Definition
A table is in 3NF if:
1. It is in 2NF
2. No transitive dependencies exist
3. Non-key attributes are not dependent on other non-key attributes

### Analysis

#### provinces Table
✅ **3NF Compliant**
- Primary key: `province_id`
- Non-key attributes: `province_name`, `security_level`
- No transitive dependencies:
  - `province_name` depends only on `province_id`
  - `security_level` depends only on `province_id`
- No non-key attribute depends on another non-key attribute

#### customers Table
✅ **3NF Compliant**
- Primary key: `customer_id`
- Non-key attributes: All customer attributes
- No transitive dependencies:
  - All attributes directly depend on `customer_id`
  - No attribute depends on another non-key attribute
  - `province_id` (foreign key) depends on `customer_id`, not on other customer attributes
- Proper separation of concerns: Province data is in the `provinces` table, not repeated in `customers`

#### customer_risk_history Table
✅ **3NF Compliant**
- Primary key: `id`
- Non-key attributes: `customer_id`, `risk_score`, `recorded_at`
- No transitive dependencies:
  - `customer_id` depends only on `id`
  - `risk_score` depends only on `id`
  - `recorded_at` depends only on `id`
- No non-key attribute depends on another non-key attribute

### 3NF Conclusion
**Status:** ✅ **PASS**

All tables satisfy Third Normal Form requirements. No transitive dependencies exist, and all non-key attributes depend directly on the primary key.

---

## Normalization Summary

| Table | 1NF | 2NF | 3NF | Overall Status |
|-------|-----|-----|-----|---------------|
| provinces | ✅ | ✅ | ✅ | Fully Normalized |
| customers | ✅ | ✅ | ✅ | Fully Normalized |
| customer_risk_history | ✅ | ✅ | ✅ | Fully Normalized |

---

## Benefits of Normalization

### Data Integrity
- ✅ Eliminates update anomalies
- ✅ Prevents insertion anomalies
- ✅ Avoids deletion anomalies

### Data Consistency
- ✅ Single source of truth for provinces
- ✅ No redundant customer data
- ✅ Consistent risk history tracking

### Storage Efficiency
- ✅ Minimal data redundancy
- ✅ Efficient storage utilization
- ✅ Optimized for query performance

### Maintainability
- ✅ Clear separation of concerns
- ✅ Easy to modify business rules
- ✅ Simplified schema evolution

---

## Denormalization Considerations

### Current State
The database is fully normalized (3NF), which is appropriate for this application because:

1. **Read-Write Balance:** The application has both read (analytics, reports) and write (customer updates, risk recording) operations
2. **Data Integrity:** Churn prediction requires accurate, consistent data
3. **Moderate Dataset Size:** 15,000 customers with periodic risk history additions
4. **Query Patterns:** Most queries are filtered by customer_id, province_id, or time ranges

### Potential Denormalization (Future Considerations)
If performance issues arise with large-scale deployments, consider:

1. **Materialized Views:** For province-level analytics
2. **Computed Columns:** For frequently calculated metrics (health score, risk level)
3. **Summary Tables:** For dashboard KPI aggregations

**Current Recommendation:** Maintain 3NF for data integrity. Add denormalization only if performance testing indicates a need.

---

## Normalization Best Practices Applied

### ✅ Proper Primary Keys
- All tables have auto-incrementing integer primary keys
- Primary keys are single-column for simplicity

### ✅ Foreign Key Relationships
- All relationships properly defined with CASCADE rules
- Referential integrity enforced at database level

### ✅ Atomic Values
- No multi-valued attributes
- No nested structures
- No repeating groups

### ✅ No Redundancy
- Province data stored once in `provinces` table
- Customer data not duplicated across tables
- Risk history tracks changes without duplicating customer data

### ✅ Appropriate Data Types
- INT for numeric identifiers and counts
- VARCHAR for text fields with appropriate lengths
- FLOAT for decimal values (rates, amounts)
- DATETIME for timestamps
- TINYINT for boolean flags (churn)

---

## Conclusion

The database schema is **fully normalized to Third Normal Form (3NF)**. This ensures:

- **Data Integrity:** No anomalies in insert, update, or delete operations
- **Consistency:** Single source of truth for all data
- **Maintainability:** Clear structure that is easy to understand and modify
- **Performance:** Appropriate indexing strategy for query optimization

**Recommendation:** Maintain current normalized structure. Consider denormalization only if performance testing identifies specific bottlenecks in production.

**Normalization Score:** 10/10 ✅ **Excellent**
