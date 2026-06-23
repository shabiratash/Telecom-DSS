# Project Structure Review

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Date:** June 22, 2026
**Purpose:** Evaluate and recommend improvements to project folder organization

---

## Current Structure

```
e:\Projects\NEW\
├── app.py                          # Flask application factory
├── config.py                       # Configuration settings
├── constants.py                    # Province and feature definitions
├── extensions.py                   # Database extensions
├── generate_dataset.py            # Dataset generation script
├── seed_db.py                      # Database seeding script
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (credentials)
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # Main documentation
├── dataset/                        # Dataset directory
│   └── telecom_dataset.csv         # Training dataset (15,000 records)
├── docs/                           # Documentation
│   ├── API.md
│   ├── DATABASE_SCHEMA.md
│   ├── DATA_DICTIONARY.md
│   ├── ERD.md
│   ├── ERD_MERMAID.md
│   ├── CODEBASE_AUDIT.md
│   ├── CLEANUP_REPORT.md
│   ├── DATABASE_REVIEW.md
│   ├── NORMALIZATION.md
│   ├── THESIS_DIAGRAMS.md
│   └── PROJECT_STRUCTURE_REVIEW.md
├── ml/                             # Machine learning module
│   ├── __init__.py
│   ├── train.py
│   ├── predictor.py
│   └── recommendations.py
├── models/                         # SQLAlchemy models
│   ├── __init__.py
│   ├── province.py
│   ├── customer.py
│   ├── training_history.py
│   └── customer_risk_history.py
├── models_ml/                      # Trained models
│   └── churn_model.pkl
├── routes/                         # Flask route controllers
│   ├── __init__.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── customer.py
│   ├── prediction.py
│   ├── analytics.py
│   ├── reports.py
│   ├── ml_center.py
│   ├── whatif_simulator.py
│   ├── early_warning.py
│   ├── financial_impact.py
│   └── helpers.py
├── sql/                            # SQL scripts
│   ├── schema.sql
│   ├── seed_provinces.sql
│   └── add_customer_risk_history.sql
├── static/                         # Static assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── charts.js
│   │   ├── ml_center.js
│   │   ├── whatif_simulator.js
│   │   ├── early_warning.js
│   │   └── financial_impact.js
│   └── uploads/
└── templates/                      # Jinja2 templates
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── customers.html
    ├── add_customer.html
    ├── edit_customer.html
    ├── profile.html
    ├── prediction.html
    ├── analytics.html
    ├── early_warning.html
    ├── financial_impact.html
    ├── _customer_form.html
    ├── _customer_form_predict.html
    ├── ml_center/
    │   └── index.html
    └── whatif_simulator/
        └── index.html
```

---

## Structure Analysis

### ✅ Strengths

1. **Clear Separation of Concerns**
   - Routes, models, templates, and static files are properly separated
   - ML module is isolated from application logic
   - Database models are in dedicated directory

2. **Modular Design**
   - Each feature has its own route file
   - Templates organized with subdirectories for complex features
   - Static assets separated by type (CSS, JS)

3. **Documentation**
   - Comprehensive docs directory
   - SQL scripts in dedicated folder
   - README at root level

4. **Configuration Management**
   - Environment variables properly handled
   - Configuration separated from application code

### ⚠️ Areas for Improvement

1. **Root Directory Clutter**
   - Multiple Python files at root level (app.py, config.py, constants.py, etc.)
   - Could be grouped into an `app/` directory

2. **Missing Tests Directory**
   - No dedicated `tests/` directory
   - No unit tests, integration tests, or test fixtures

3. **Mixed Responsibilities**
   - `generate_dataset.py` and `seed_db.py` are scripts, not application code
   - Could be moved to `scripts/` directory

4. **ML Module Location**
   - `ml/` and `models/` could be confusing (ML models vs database models)
   - Consider renaming `models_ml/` to `trained_models/` for clarity

---

## Recommended Structure

```
e:\Projects\NEW\
├── app/                            # Application package
│   ├── __init__.py
│   ├── app.py                      # Flask application factory
│   ├── config.py                   # Configuration settings
│   ├── constants.py                # Province and feature definitions
│   ├── extensions.py               # Database extensions
│   ├── routes/                     # Flask route controllers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── customer.py
│   │   ├── prediction.py
│   │   ├── analytics.py
│   │   ├── reports.py
│   │   ├── ml_center.py
│   │   ├── whatif_simulator.py
│   │   ├── early_warning.py
│   │   ├── financial_impact.py
│   │   └── helpers.py
│   ├── models/                     # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── province.py
│   │   ├── customer.py
│   │   ├── training_history.py
│   │   └── customer_risk_history.py
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── customer_service.py
│   │   ├── prediction_service.py
│   │   └── analytics_service.py
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── ml/                             # Machine learning module
│   ├── __init__.py
│   ├── train.py
│   ├── predictor.py
│   └── recommendations.py
├── trained_models/                 # Trained ML models
│   └── churn_model.pkl
├── database/                       # Database-related files
│   ├── schema.sql
│   ├── seed_provinces.sql
│   └── add_customer_risk_history.sql
├── datasets/                       # Datasets
│   └── telecom_dataset.csv
├── scripts/                        # Utility scripts
│   ├── generate_dataset.py
│   └── seed_db.py
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_routes/
│   ├── test_models/
│   ├── test_services/
│   └── fixtures/
├── static/                         # Static assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── charts.js
│   │   ├── ml_center.js
│   │   ├── whatif_simulator.js
│   │   ├── early_warning.js
│   │   └── financial_impact.js
│   └── uploads/
├── templates/                      # Jinja2 templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── customers.html
│   ├── add_customer.html
│   ├── edit_customer.html
│   ├── profile.html
│   ├── prediction.html
│   ├── analytics.html
│   ├── early_warning.html
│   ├── financial_impact.html
│   ├── _customer_form.html
│   ├── _customer_form_predict.html
│   ├── ml_center/
│   │   └── index.html
│   └── whatif_simulator/
│       └── index.html
├── docs/                           # Documentation
│   ├── API.md
│   ├── DATABASE_SCHEMA.md
│   ├── DATA_DICTIONARY.md
│   ├── ERD.md
│   ├── ERD_MERMAID.md
│   ├── CODEBASE_AUDIT.md
│   ├── CLEANUP_REPORT.md
│   ├── DATABASE_REVIEW.md
│   ├── NORMALIZATION.md
│   ├── THESIS_DIAGRAMS.md
│   ├── PROJECT_STRUCTURE_REVIEW.md
│   └── SYSTEM_TESTING.md
├── .env                            # Environment variables
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── requirements.txt                 # Python dependencies
└── README.md                       # Main documentation
```

---

## Migration Plan

### Phase 1: Create New Directories
```powershell
mkdir app
mkdir app\services
mkdir app\utils
mkdir database
mkdir datasets
mkdir scripts
mkdir tests
mkdir tests\test_routes
mkdir tests\test_models
mkdir tests\test_services
mkdir tests\fixtures
mkdir trained_models
```

### Phase 2: Move Files
```powershell
# Move application files to app/
move app.py app\
move config.py app\
move constants.py app\
move extensions.py app\

# Move routes to app/routes/
move routes\* app\routes\

# Move models to app/models/
move models\* app\models\

# Move SQL files to database/
move sql\* database\

# Move dataset to datasets/
move dataset\telecom_dataset.csv datasets\

# Move scripts to scripts/
move generate_dataset.py scripts\
move seed_db.py scripts\

# Move trained models
move models_ml trained_models
```

### Phase 3: Update Imports
- Update all `from routes.` to `from app.routes.`
- Update all `from models.` to `from app.models.`
- Update all imports in `app.py`
- Update sys.path in `app.py` to include `app/` directory

### Phase 4: Create Service Layer (Optional)
- Extract business logic from routes into `app/services/`
- Create `customer_service.py`, `prediction_service.py`, `analytics_service.py`
- Update routes to use services

### Phase 5: Create Tests (Optional)
- Create test files in `tests/`
- Write unit tests for models, services, and routes
- Add test fixtures in `tests/fixtures/`

---

## Import Changes Required

### Current Imports
```python
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from models import Customer, Province
```

### New Imports
```python
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.models import Customer, Province
```

### Files Requiring Import Updates
- `app/app.py`
- `app/routes/*.py`
- `app/services/*.py` (if created)
- `tests/*.py` (if created)

---

## Risk Assessment

### Low Risk
- Moving files to new directories
- Renaming directories
- Creating new empty directories

### Medium Risk
- Updating import statements
- Modifying `app.py` to handle new structure
- Potential path resolution issues

### High Risk
- None identified

---

## Recommendation

### Option 1: Minimal Restructuring (Recommended for Thesis)
**Keep current structure** with minor improvements:
- Rename `models_ml/` to `trained_models/`
- Create empty `tests/` directory for future use
- Move `generate_dataset.py` and `seed_db.py` to `scripts/`
- Add `app/__init__.py` and move core files if needed

**Pros:**
- Minimal risk of breaking functionality
- Less work required
- No import changes needed
- Thesis deadline considerations

**Cons:**
- Root directory still has multiple files
- Not ideal for long-term maintainability

### Option 2: Full Restructuring (Recommended for Production)
**Implement recommended structure** with all migrations

**Pros:**
- Better organization
- Industry-standard structure
- Easier to maintain and scale
- Clear separation of concerns

**Cons:**
- Higher risk of breaking functionality
- More work required
- Import changes needed
- May delay thesis submission

---

## Decision

**For Thesis Submission:** Option 1 (Minimal Restructuring)
- Rename `models_ml/` to `trained_models/`
- Create `scripts/` directory and move scripts
- Create empty `tests/` directory
- Keep current file locations otherwise

**For Production Deployment:** Option 2 (Full Restructuring)
- Implement full recommended structure
- Complete all migration phases
- Add comprehensive test suite

---

## Next Steps

### Immediate (Thesis-Ready)
1. Rename `models_ml/` to `trained_models/`
2. Create `scripts/` directory
3. Move `generate_dataset.py` and `seed_db.py` to `scripts/`
4. Create empty `tests/` directory
5. Update imports in affected files

### Post-Thesis (Production-Ready)
1. Implement full restructuring
2. Create service layer
3. Add comprehensive tests
4. Update all imports
5. Test thoroughly

---

## Conclusion

The current structure is functional and well-organized for a thesis project. The recommended restructuring would improve long-term maintainability but introduces risk. For thesis submission, minimal restructuring is recommended. For production deployment, full restructuring should be implemented.

**Current Structure Score:** 7/10 ✅ Good
**Recommended Structure Score:** 9/10 ✅ Excellent
