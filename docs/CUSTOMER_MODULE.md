# Customer Module (Customer Workspace)

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Module:** Customer Workspace (mini-CRM)
**Type:** Enhancement of the existing `customer` blueprint (no duplication)

---

## Purpose

The Customer Workspace is a dedicated, visually-separated mini-CRM for managing
and analysing individual customers. It reuses the existing `customer` blueprint,
models, and business logic — no tables or logic are duplicated — but presents
them through their own layout and sidebar, separate from the main dashboard.

---

## Architecture

```
routes/customer.py (existing blueprint, enhanced)
  Pages (HTML):
    GET  /customers                      -> Customer List      (list.html)
    GET  /customers/add                  -> Add Customer       (add.html)
    GET  /customers/<id>/edit            -> Edit Customer      (edit.html)
    GET  /customers/view/<id>            -> Quick View         (view.html)        [NEW]
    GET  /customers/profile/<id>         -> Full CRM Profile   (profile.html)     [NEW]
    GET  /customers/<id>                 -> redirects to profile/<id>  (backward compatible)
    GET  /customers/prediction-history   -> Prediction History (prediction_history.html) [NEW]
    GET  /customers/risk-history         -> Risk History       (risk_history.html)       [NEW]
    GET  /customers/recommendations      -> Recommendations    (recommendations.html)    [NEW]
    GET  /customers/health-scores        -> Health Scores      (health_scores.html)      [NEW]
    GET  /customers/live-monitor         -> Live Monitor       (live_monitor.html)       [NEW]
  JSON APIs:
    GET  /api/customers/live-monitor
    GET  /api/customers/<id>/prediction-history
    GET  /api/customers/<id>/recommendation-history
    GET  /api/customers/<id>/risk-history

templates/customer_workspace/   (separate layout + sidebar)
  base.html  list.html  add.html  edit.html  view.html  profile.html
  prediction_history.html  risk_history.html  recommendations.html
  health_scores.html  live_monitor.html

static/js/customer_profile.js   (profile timelines + history tables)
static/js/live_monitor.js       (auto-refresh live feed)
```

### Separation
- **Own layout:** `customer_workspace/base.html` is a standalone HTML shell.
- **Own sidebar:** Customer List, Add Customer, Health Scores, Prediction History,
  Risk History, Retention Recommendations, Live Customer Monitor, plus links back
  to the main dashboard.
- **Own templates:** all under `templates/customer_workspace/`.
- The main **Dashboard** now shows a summary card linking into the workspace.

### Reuse (no duplication)
- Uses the existing `Customer`, `Province`, `CustomerRiskHistory` models.
- Uses `ml.predictor.predict()` for predictions (unchanged).
- Uses `Customer.health_score()` / `health_status()` (unchanged).

---

## Customer Profile (`/customers/profile/<id>`)

Sections displayed:

1. **Personal Information** — age, gender, province, area type
2. **Network Information** — quality, internet type, call drop rate, tower availability
3. **Usage Statistics** — recharge, frequency, tenure, inactivity, complaints, discounts
4. **Prediction History** — table sourced from `prediction_log`
5. **Risk Score History** — line chart sourced from `customer_risk_history`
6. **Retention Recommendation History** — table sourced from `recommendation_log`
7. **Customer Health Score** — score + status badge
8. **Churn Probability Timeline** — line chart from `prediction_log`

Opening a profile triggers a fresh prediction which is logged (audit trail).

---

## Live Customer Monitor (`/customers/live-monitor`)

Auto-refreshes every 5 seconds. Controls: **Refresh**, **Pause**, **Resume**.

Panels:
- Newly Added Customers
- Recently Predicted Customers (from `prediction_log`)
- High-Risk Customers
- Recent Recommendations (from `recommendation_log`)
- Recent Database Updates (risk scores from `customer_risk_history`)

---

## Database Integration

- Reads existing tables: `customers`, `provinces`, `customer_risk_history`.
- Reads additive log tables: `prediction_log`, `recommendation_log`
  (see `docs/REALTIME_DATA_VIEWER.md` and `sql/add_logging_tables.sql`).
- Writes: only prediction/recommendation audit logs via `services/logging_service.py`.
- **No existing table is altered or duplicated.**

---

## Workflow

1. From the Dashboard, click **Open Workspace** → `/customers`.
2. Browse/search/paginate customers (server-side pagination preserved).
3. Open a customer profile → prediction runs and is logged → timelines render.
4. Use the workspace sidebar to review global histories or the live monitor.

---

## Screenshots (placeholders)

- _[Screenshot: Customer List with workspace sidebar]_
- _[Screenshot: Full customer profile with timelines]_
- _[Screenshot: Live customer monitor]_
- _[Screenshot: Health scores page]_

---

## Safety Notes

- Existing routes preserved; `/customers/<id>` still works (redirects to profile).
- No customer table duplication; existing models reused.
- Backward compatible; only additive routes/templates/JS were introduced.
