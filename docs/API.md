# API Documentation

All routes require an authenticated admin session (cookie-based). JSON endpoints
are prefixed with `/api`. Unauthenticated requests are redirected to `/login`.

## Authentication
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/login` | Admin login form / submit |
| GET | `/logout` | Clear session |

## Pages (HTML)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard` | Main dashboard |
| GET | `/customers` | Customer list (query: `page`, `search`, `province_id`, `churn`, `network_quality`) |
| GET/POST | `/customers/add` | Add customer |
| GET/POST | `/customers/<id>/edit` | Edit customer |
| POST | `/customers/<id>/delete` | Delete customer |
| GET | `/customers/<id>` | Customer profile + prediction |
| GET/POST | `/prediction` | Prediction form |
| GET | `/analytics` | Analytics & model insights |
| POST | `/analytics/train` | Train / retrain the model |

## Dashboard JSON
| Method | Path | Response |
|--------|------|----------|
| GET | `/api/dashboard/summary` | KPI object |
| GET | `/api/dashboard/churn-split` | `{labels, values}` |
| GET | `/api/dashboard/province-customers` | `{labels, values}` |
| GET | `/api/dashboard/monthly-trend` | `{labels, values}` |
| GET | `/api/dashboard/province-stats` | `[{province, security_level, customers, churned, churn_rate}]` |

## Prediction JSON
| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | `/api/predict` | feature dict (JSON or form) | `{prediction, prediction_label, probability, risk_level, recommendations[]}` |

### Example
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  --cookie "session=<your-session-cookie>" \
  -d '{
    "age": 28, "gender": "Male", "province_name": "Kabul",
    "area_type": "Urban", "network_quality": "Poor", "internet_type": "3G",
    "call_drop_rate": 12, "recharge_amount": 80, "recharge_frequency": 2,
    "payment_method": "Cash", "tenure_months": 4, "inactive_days": 45,
    "complaint_count": 5, "tower_availability": "Low",
    "competitor_offer_exposure": "Yes", "discount_usage": "No"
  }'
```
```json
{
  "prediction": 1,
  "prediction_label": "Customer will Churn",
  "probability": 88.42,
  "risk_level": "High",
  "recommendations": [
    {"title": "Critical Churn Risk", "action": "...", "severity": "high", "icon": "bi-exclamation-octagon"}
  ]
}
```

## Analytics JSON
| Method | Path | Response |
|--------|------|----------|
| GET | `/api/analytics/model` | metrics, confusion matrix, ROC, feature importance |
| GET | `/api/analytics/feature-importance` | `{labels, values}` |
| GET | `/api/analytics/province` | `[{province, customers, churn_rate}]` |
| GET | `/api/analytics/complaints` | `{labels, values}` |
| GET | `/api/analytics/segmentation` | `{labels, values}` |
| GET | `/api/analytics/top-risk` | `[{customer_id, province, risk_score, ...}]` |
| GET | `/api/analytics/heatmap` | `{provinces, networks, matrix}` |

## Reports
| Method | Path | Output |
|--------|------|--------|
| GET | `/reports/csv` | CSV of all customers |
| GET | `/reports/excel` | XLSX (Summary, Provinces, Customers) |
| GET | `/reports/pdf` | PDF analytics + model report |
