# Codebase Audit Report

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Date:** June 22, 2026
**Purpose:** Identify unused, duplicate, and obsolete files for safe cleanup

---

## Safe to Delete (YES)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `__pycache__/` | Root directory | Python bytecode cache directory | YES |
| `*.pyc` files | All directories | Python bytecode files | YES |
| `.sixth/` | Root directory | IDE-specific directory (Cascade/Sixth) | YES |
| `.venv/` | Root directory | Virtual environment (should be in .gitignore) | YES |
| `README.pdf` | Root directory | Duplicate of README.md | YES |
| `README.txt` | Root directory | Duplicate of README.md | YES |
| `dataset.zip` | Root directory | Duplicate - dataset already in dataset/ directory | YES |

---

## Keep - Core Application Files (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `app.py` | Root directory | Flask application factory - main entry point | NO |
| `config.py` | Root directory | Configuration settings | NO |
| `constants.py` | Root directory | Province and feature definitions | NO |
| `extensions.py` | Root directory | Database extensions | NO |
| `generate_dataset.py` | Root directory | Dataset generation script | NO |
| `seed_db.py` | Root directory | Database seeding script | NO |
| `requirements.txt` | Root directory | Python dependencies | NO |
| `.env` | Root directory | Environment variables (contains credentials) | NO |
| `.env.example` | Root directory | Environment variables template | NO |
| `.gitignore` | Root directory | Git ignore rules | NO |

---

## Keep - Routes (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `auth.py` | routes/ | Authentication routes - imported in app.py | NO |
| `dashboard.py` | routes/ | Dashboard routes - imported in app.py | NO |
| `customer.py` | routes/ | Customer management routes - imported in app.py | NO |
| `prediction.py` | routes/ | Prediction routes - imported in app.py | NO |
| `analytics.py` | routes/ | Analytics routes - imported in app.py | NO |
| `reports.py` | routes/ | Report generation routes - imported in app.py | NO |
| `ml_center.py` | routes/ | ML Center routes - imported in app.py | NO |
| `whatif_simulator.py` | routes/ | What-If Simulator routes - imported in app.py | NO |
| `early_warning.py` | routes/ | Early Warning System routes - imported in app.py | NO |
| `financial_impact.py` | routes/ | Financial Impact routes - imported in app.py | NO |
| `helpers.py` | routes/ | Helper functions (login_required) - used by all routes | NO |
| `__init__.py` | routes/ | Package initialization | NO |

---

## Keep - Models (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `province.py` | models/ | Province model - imported in models/__init__.py | NO |
| `customer.py` | models/ | Customer model - imported in models/__init__.py | NO |
| `training_history.py` | models/ | Model training history - imported in models/__init__.py | NO |
| `customer_risk_history.py` | models/ | Customer risk history - imported in models/__init__.py | NO |
| `__init__.py` | models/ | Package initialization | NO |

---

## Keep - ML Module (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `train.py` | ml/ | Model training script | NO |
| `predictor.py` | ml/ | Prediction service - used by prediction routes | NO |
| `recommendations.py` | ml/ | Retention recommendations - used by predictor | NO |
| `__init__.py` | ml/ | Package initialization | NO |

---

## Keep - Trained Models (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `churn_model.pkl` | models_ml/ | Trained ML model - required for predictions | NO |

---

## Keep - Dataset (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `telecom_dataset.csv` | dataset/ | Training dataset - 15,000 records | NO |

---

## Keep - SQL Files (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `schema.sql` | sql/ | Database schema - includes all tables | NO |
| `seed_provinces.sql` | sql/ | Province data seeding | NO |
| `add_customer_risk_history.sql` | sql/ | Add new table without dropping data | NO |

---

## Keep - Templates (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `base.html` | templates/ | Base template with sidebar/navigation | NO |
| `login.html` | templates/ | Login page | NO |
| `dashboard.html` | templates/ | Dashboard page | NO |
| `customers.html` | templates/ | Customer list page | NO |
| `add_customer.html` | templates/ | Add customer form | NO |
| `edit_customer.html` | templates/ | Edit customer form | NO |
| `profile.html` | templates/ | Customer profile page | NO |
| `prediction.html` | templates/ | Prediction page | NO |
| `analytics.html` | templates/ | Analytics page | NO |
| `early_warning.html` | templates/ | Early Warning System page | NO |
| `financial_impact.html` | templates/ | Financial Impact page | NO |
| `_customer_form.html` | templates/ | Customer form partial | NO |
| `_customer_form_predict.html` | templates/ | Prediction form partial | NO |
| `ml_center/index.html` | templates/ml_center/ | ML Center page | NO |
| `whatif_simulator/index.html` | templates/whatif_simulator/ | What-If Simulator page | NO |

---

## Keep - Static Files (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `style.css` | static/css/ | Main stylesheet - glassmorphism theme | NO |
| `dashboard.js` | static/js/ | Dashboard JavaScript | NO |
| `charts.js` | static/js/ | Chart.js visualizations | NO |
| `ml_center.js` | static/js/ | ML Center JavaScript | NO |
| `whatif_simulator.js` | static/js/ | What-If Simulator JavaScript | NO |
| `early_warning.js` | static/js/ | Early Warning JavaScript | NO |
| `financial_impact.js` | static/js/ | Financial Impact JavaScript | NO |
| `uploads/` | static/uploads/ | File upload directory | NO |

---

## Keep - Documentation (NO)

| File Name | Location | Reason | Safe To Delete |
|-----------|----------|--------|----------------|
| `README.md` | Root directory | Main project documentation | NO |
| `DATABASE_SCHEMA.md` | docs/ | Database schema documentation | NO |
| `DATA_DICTIONARY.md` | docs/ | Data dictionary | NO |
| `ERD.md` | docs/ | ERD documentation | NO |
| `ERD_MERMAID.md` | docs/ | Mermaid ERD diagrams | NO |
| `API.md` | docs/ | API documentation | NO |

---

## Summary

**Total Files Audited:** 60+
**Safe to Delete:** 7 files/directories
**Keep:** 53+ files/directories

**Cleanup Priority:**
1. **High Priority:** Remove Python cache (`__pycache__`, `*.pyc`)
2. **Medium Priority:** Remove duplicate README files
3. **Low Priority:** Remove IDE-specific directories (`.sixth`, `.venv`)

**Recommendation:** Execute Phase 2 cleanup only on files marked "YES" to ensure no functionality is broken.
