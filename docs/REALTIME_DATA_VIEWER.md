# Real-Time Data Viewer & Live Database Monitor

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Module:** Analytics > Real-Time Data Viewer
**Type:** Additive monitoring with audit-trail logging

---

## Purpose

Provides a live, auto-refreshing view of the newest activity across the deployed
system — latest customers, predictions, recommendations, and risk scores — plus
aggregate database counters. Backed by additive audit-trail tables so every
prediction and recommendation produced by the deployed system is captured.

---

## Architecture

```
routes/analytics.py
  GET /analytics/live-data            -> page (templates/live_data.html)
  GET /api/analytics/live-data        -> newest records feed (JSON)
  GET /api/analytics/db-monitor       -> aggregate counters (JSON)

static/js/live_data.js                -> 5s auto-refresh + pause/resume

services/logging_service.py           -> guarded writes to log tables
models/prediction_log.py              -> PredictionLog
models/recommendation_log.py          -> RecommendationLog
sql/add_logging_tables.sql            -> additive migration (CREATE TABLE IF NOT EXISTS)
```

---

## Additive Logging Tables

These tables are **new and additive**. No existing table is altered.

### prediction_log
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK | auto-increment |
| customer_id | INT NULL | FK -> customers (ON DELETE SET NULL); null for ad-hoc form predictions |
| churn_probability | FLOAT | predicted probability (%) |
| prediction | INT | 0/1 |
| prediction_label | VARCHAR(40) | human label |
| risk_level | VARCHAR(20) | Low/Medium/High |
| health_score | INT NULL | health score at time of prediction |
| source | VARCHAR(30) | single / api / batch / profile |
| created_at | DATETIME | timestamp |

### recommendation_log
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK | auto-increment |
| customer_id | INT NULL | FK -> customers (ON DELETE SET NULL) |
| prediction_id | INT NULL | FK -> prediction_log (ON DELETE CASCADE) |
| title | VARCHAR(120) | recommendation title |
| action | TEXT | recommended action |
| severity | VARCHAR(20) | high/medium/low |
| icon | VARCHAR(40) | bootstrap icon |
| created_at | DATETIME | timestamp |

### Auto-creation
`services/logging_service.py` calls `Table.create(checkfirst=True)` on first use,
so the feature works even before the SQL migration is run. The SQL migration
(`sql/add_logging_tables.sql`) is provided for explicit/production setup.

---

## What gets logged (every deployed prediction)

| Trigger | Source value | Customer link |
|---------|--------------|---------------|
| `/prediction` form submit | `single` | none (ad-hoc) |
| `/api/predict` | `api` | linked if customer saved |
| `/prediction/batch-predict` | `batch` | none (CSV rows) |
| Customer profile open | `profile` | linked |

Logging is **fully guarded** (try/except + rollback) so a logging failure can
never break a prediction, recommendation, or any route. The ML prediction logic
in `ml/predictor.py` and `ml/recommendations.py` is **unchanged**.

---

## Real-Time Data Viewer (`/analytics/live-data`)

Auto-refreshes every 5 seconds. Controls: **Refresh**, **Pause**, **Resume**.

Panels:
- Latest Customers
- Latest Predictions
- Latest Recommendations
- Latest Risk Scores

---

## Live Database Monitor

Aggregate counters (from `/api/analytics/db-monitor`):

- Total Customers
- Total Predictions
- Total High-Risk Customers
- Total Recommendations
- Records Added Today
- Records Added This Week

Counters update automatically on each refresh cycle.

---

## Workflow

1. Open **Analytics > Real-Time Data** → `/analytics/live-data`.
2. JS polls `/api/analytics/live-data` and `/api/analytics/db-monitor` every 5s.
3. Panels and counters update; user can pause/resume the live stream.
4. As predictions/recommendations are generated elsewhere in the app, they appear
   in the feed because they are logged to `prediction_log` / `recommendation_log`.

---

## Database Integration

- Writes: `prediction_log`, `recommendation_log` (additive, via logging service).
- Reads: `customers`, `provinces`, `customer_risk_history`, and the two log tables.
- **No existing tables altered or removed. Backward compatible.**

---

## Screenshots (placeholders)

- _[Screenshot: Live database monitor counters]_
- _[Screenshot: Real-time data feed panels]_
- _[Screenshot: Pause/Resume controls]_

---

## Setup

Run once on an existing database (optional — tables auto-create on first use):

```bash
mysql -u root -p telecom_churn_db < sql/add_logging_tables.sql
```
