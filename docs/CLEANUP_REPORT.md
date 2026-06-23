# Cleanup Execution Plan

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Date:** June 22, 2026
**Phase:** Phase 2 - Safe Cleanup

---

## Execution Plan

### Files to Delete (Safe)

| # | File/Directory | Type | Size Impact | Risk Level |
|---|----------------|------|-------------|------------|
| 1 | `__pycache__/` (root) | Directory | ~50KB | NONE |
| 2 | `__pycache__/` (ml/) | Directory | ~20KB | NONE |
| 3 | `__pycache__/` (models/) | Directory | ~20KB | NONE |
| 4 | `__pycache__/` (routes/) | Directory | ~30KB | NONE |
| 5 | `*.pyc` files (all) | Files | ~120KB | NONE |
| 6 | `.sixth/` | Directory | ~5KB | NONE |
| 7 | `.venv/` | Directory | ~500MB | LOW* |
| 8 | `README.pdf` | File | ~4KB | NONE |
| 9 | `README.txt` | File | ~4KB | NONE |
| 10 | `dataset.zip` | File | ~9MB | NONE |

*\* .venv/ contains virtual environment - should be in .gitignore but safe to delete as it can be recreated*

---

## Deletion Commands

### Python Cache Removal
```powershell
# Remove all __pycache__ directories
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force ml\__pycache__
Remove-Item -Recurse -Force models\__pycache__
Remove-Item -Recurse -Force routes\__pycache__

# Remove all .pyc files
Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force
```

### IDE and Duplicate Files
```powershell
# Remove IDE-specific directory
Remove-Item -Recurse -Force .sixth

# Remove duplicate README files
Remove-Item README.pdf
Remove-Item README.txt

# Remove duplicate dataset zip
Remove-Item dataset.zip
```

### Virtual Environment (Optional)
```powershell
# Remove virtual environment (can be recreated)
Remove-Item -Recurse -Force .venv
```

---

## Impact Assessment

### No Impact On:
- ✅ Application functionality
- ✅ Database schema
- ✅ Trained models
- ✅ Datasets
- ✅ Routes and controllers
- ✅ Templates
- ✅ Static assets
- ✅ Configuration
- ✅ ML prediction logic

### What Will Be Removed:
- Python bytecode cache (auto-generated on import)
- IDE-specific metadata
- Duplicate documentation files
- Duplicate dataset archive
- Virtual environment (recreatable via `python -m venv .venv`)

---

## Rollback Plan

If deletion causes issues:

1. **Python cache** - Will be regenerated automatically on next import
2. **README files** - Can be restored from git history if needed
3. **dataset.zip** - Can be recreated from `dataset/telecom_dataset.csv`
4. **.venv** - Recreate with `python -m venv .venv && pip install -r requirements.txt`
5. **.sixth** - IDE will recreate automatically

---

## Approval Required

**Status:** ⏳ PENDING APPROVAL

**Please confirm before proceeding:**
- Delete Python cache directories? (YES/NO)
- Delete duplicate README files? (YES/NO)
- Delete duplicate dataset.zip? (YES/NO)
- Delete .sixth directory? (YES/NO)
- Delete .venv directory? (YES/NO)

**Execute cleanup only after user approval.**
