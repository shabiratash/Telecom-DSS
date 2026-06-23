# Model Diagnostics Module

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Module:** Analytics > Model Diagnostics
**Type:** Read-only monitoring (no retraining)

---

## Purpose

The Model Diagnostics module provides transparency into the health and quality
of the deployed churn-prediction model. It surfaces an **overfitting signal**
and the model's **classification performance** without ever retraining or
modifying the production model.

It answers two questions for the thesis/operator:

1. Is the model overfitting (memorising training data)?
2. How well does the model perform on unseen data?

---

## Architecture

```
Analytics Blueprint (routes/analytics.py)
  ├── GET /analytics/model-diagnostics      -> page (templates/model_diagnostics.html)
  └── GET /api/analytics/diagnostics         -> JSON (ml/diagnostics.compute_diagnostics)

ml/diagnostics.py  (READ-ONLY)
  ├── loads churn_model.pkl via ml.predictor.load_bundle()
  ├── reloads dataset, recreates the SAME split (random_state=42, stratify)
  ├── predict-only on train / validation / test partitions (NO .fit)
  └── returns overfitting gap + performance + confusion matrix + ROC curve

static/js/model_diagnostics.js
  └── renders KPI cards, status pill, confusion matrix bar, ROC line chart
```

### Why this is safe (no retraining)
The existing fitted `Pipeline` is loaded from `churn_model.pkl` and only
`predict_proba` is called. The deterministic `train_test_split(random_state=42)`
recreates the exact partitions used during training so the metrics are
consistent. **No estimator is ever refit.**

---

## Overfitting Detector

| Metric | Source |
|--------|--------|
| Training Accuracy | predict-only on the training partition (data the model saw) |
| Validation Accuracy | predict-only on a validation slice carved from training data |
| Test Accuracy | predict-only on the 20% holdout (unseen) |

**Gap = Training Accuracy − Test Accuracy**

| Gap | Status |
|-----|--------|
| `< 5%` | Healthy |
| `5% – 10%` | Warning |
| `> 10%` | Potential Overfitting |

Results display as dashboard cards with a colour-coded status pill.

---

## Model Performance

Computed predict-only on the test holdout:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC AUC

### Visual Charts
- **Confusion Matrix** — TN / FP / FN / TP bar chart
- **ROC Curve** — true-positive vs false-positive rate, with random baseline

---

## Workflow

1. User opens **Analytics > Model Diagnostics**.
2. Page calls `GET /api/analytics/diagnostics`.
3. `ml/diagnostics.compute_diagnostics()` loads the model + dataset, evaluates predict-only.
4. JSON returns overfitting block, performance block, confusion matrix, ROC curve.
5. JavaScript renders KPI cards, status pill, and the two charts.

---

## Database Integration

This module is **read-only** with respect to the database. It reads the dataset
CSV and the trained model file. It does not write to any table.

---

## Screenshots (placeholders)

- _[Screenshot: Overfitting detector cards with status pill]_
- _[Screenshot: Performance KPI row]_
- _[Screenshot: Confusion matrix chart]_
- _[Screenshot: ROC curve chart]_

---

## Safety Notes

- Does **not** retrain or modify the model.
- Does **not** change prediction logic or existing APIs.
- Purely additive: new routes, one read-only module, one template, one JS file.
