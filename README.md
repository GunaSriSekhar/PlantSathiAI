# 🌿 PlantSathi AI

> **Production-Oriented AI Plant Identification and Disease Diagnosis Platform**  
> *B.Tech Computer Science (AI & Data Science) Minor Project*

PlantSathi AI is a production-grade full-stack computer vision application engineered to identify plant species and diagnose foliar plant diseases from uploaded photographs or live camera captures.

---

## 🚀 Key Highlights & Architectural Distinctions

1. **Dual Independent CV Pipelines:** Plant species identification is strictly decoupled from plant disease diagnosis. They are two separate classification tasks with independent vision backbones.
2. **Real Pretrained ML Models:**
   * **Plant Identification:** Vision Transformer (ViT) pipeline (`umutbozdag/plant-identity`) predicting botanical species.
   * **Disease Diagnosis:** PlantVillage MobileNetV2 architecture (`linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`) trained on 54,305 leaf images across 38 classes.
3. **Calibrated Uncertainty & Out-of-Distribution Handling:** Conservative threshold policies warn when a photo has ambiguous symptoms, insufficient focus, or belongs to an unsupported crop.
4. **Transparent AI Plant Doctor:** A context-aware agronomic assistant providing evidence-based care guidelines without faking LLM hallucination.
5. **Persistent History:** SQLite database managed via asynchronous SQLAlchemy ORM (`aiosqlite`) tracking full scan telemetry.
6. **Zero API Key Requirement:** The platform runs 100% locally with open-source checkpoints.

---

## 🛠️ Technology Stack

* **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React, React Router v6.
* **Backend:** FastAPI, Uvicorn, Pydantic v2, Pillow, NumPy, PyTorch / Transformers.
* **Database:** SQLite (local async with SQLAlchemy 2.0).
* **Testing:** Pytest & pytest-asyncio (backend), Vitest (frontend).

---

## 📦 Project Structure

```
plantsathi/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic settings & env management
│   │   │   └── logging_config.py    # Structured logging
│   │   ├── api/routes/              # REST endpoint controllers
│   │   │   ├── health.py            # Health & model telemetry
│   │   │   ├── analyze.py           # Combined dual-pipeline analysis
│   │   │   ├── identification.py    # Plant species identification
│   │   │   ├── diagnosis.py         # Disease screening
│   │   │   ├── scans.py             # Scan history CRUD
│   │   │   ├── chat.py              # AI Plant Doctor
│   │   │   └── plants.py            # Saved plant bookmarks
│   │   ├── ml/                      # Model loading & preprocessing
│   │   │   ├── model_loader.py      # Thread-safe singleton model cache
│   │   │   ├── model_registry.py    # Class labels & metadata
│   │   │   └── preprocessing.py     # Image normalization & scaling
│   │   ├── models/                  # SQLAlchemy ORM entities
│   │   ├── repositories/            # Database CRUD repository layer
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   └── services/                # Business logic & CV execution
│   ├── tests/                       # Unit & integration test suites
│   ├── pyproject.toml               # Python dependencies
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/              # UI components, layout, and scanner
│   │   ├── pages/                   # All 9 platform pages
│   │   ├── services/                # Axios API client
│   │   ├── hooks/                   # Custom React hooks
│   │   └── types/                   # TypeScript interfaces
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docs/                            # Architectural & technical specs
└── docker-compose.yml
```

---

## ⚡ Quickstart Guide (Local Development)

### Prerequisites
* Python 3.11+ (or Python managed via `uv`)
* Node.js 18+ & npm

### 1. Start the Backend

Open a PowerShell terminal:
```powershell
cd backend

# Option A: Using uv (Fastest)
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option B: Standard pip & python
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend API interactive documentation will be available at: `http://localhost:8000/api/docs`.

### 2. Start the Frontend

In a second terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 Running the Tests

### Backend Tests:
```powershell
cd backend
uv run pytest tests/ -v
```

### Frontend Tests:
```powershell
cd frontend
npm test
```

---

## 🛡️ Academic & Scientific Transparency

* **No Hallucinated Accuracies:** We avoid unsupported statements like "99% accuracy" without a reproducible held-out test evaluation. The model status dashboard explicitly states *"Evaluation not yet completed locally"* for transparency.
* **Separation of Concerns:** A plant disease classifier trained on 14 specific agricultural crops does not claim to diagnose unsupported decorative houseplants without notifying the user.
