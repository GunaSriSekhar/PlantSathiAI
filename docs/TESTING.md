# PlantSathi AI — Automated Testing Guide

## 1. Test Architecture

The testing suite distinguishes unit tests with mocked inference from end-to-end integration tests with real weights.

* **Unit Tests (`tests/unit/`):** Fast, mocked execution covering health checks, image validation, confidence logic, label parsing, crop support filtering, and repository CRUD.
* **Integration Tests (`tests/integration/`):** Exercises the FastAPI endpoints (`/api/analyze`, `/api/scans`, etc.) end-to-end.
* **Real Model Tests (Marked with `@pytest.mark.real_model`):** Tests actual model execution against physical weights.

---

## 2. Running Backend Tests

Using `uv` (recommended):
```powershell
cd backend
uv run pytest tests/ -v
```

To run only unit tests (excluding real model downloads):
```powershell
uv run pytest tests/unit/ -v -m "not real_model"
```

To generate a test coverage report:
```powershell
uv run pytest --cov=app tests/
```

---

## 3. Running Frontend Tests

Using `npm` or `pnpm`:
```powershell
cd frontend
npm test
```
