# PlantSathi AI — REST API Specification

FastAPI documentation is automatically available interactively at:
* Swagger UI: `http://localhost:8000/api/docs`
* ReDoc: `http://localhost:8000/api/redoc`

---

## Endpoints Summary

### 1. Health & Telemetry
* `GET /api/health`
  * Returns: `{ "status": "ok", "app_name": "PlantSathi AI", "version": "0.1.0", "timestamp": "..." }`
* `GET /api/models/status`
  * Returns: List of active models, loaded compute device, class counts, and memory status.

### 2. Analysis & Inference
* `POST /api/analyze?save=true`
  * **Payload:** `multipart/form-data` with `file: UploadFile`
  * **Response:**
  ```json
  {
    "scan_id": "uuid",
    "created_at": "2026-10-28T...",
    "plant": {
      "common_name": "Tomato",
      "confidence": 0.82,
      "confidence_level": "high",
      "reliable": true,
      "supported": true,
      "candidates": [{"label": "Tomato", "score": 0.82, "rank": 1}]
    },
    "disease": {
      "status": "identified",
      "label": "Tomato___Early_blight",
      "crop": "Tomato",
      "disease_name": "Early Blight",
      "is_healthy": false,
      "confidence": 0.78,
      "confidence_level": "medium",
      "supported": true
    },
    "recommendations": [
      {
        "category": "Treatment",
        "title": "Apply copper-based fungicide",
        "description": "Spray copper hydroxide or copper oxychloride...",
        "urgency": "high"
      }
    ],
    "warnings": [],
    "models": {
      "identification": "umutbozdag/plant-identity",
      "diagnosis": "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    },
    "analysis_duration_ms": 312.4
  }
  ```

* `POST /api/identify`
  * Dedicated species identification pipeline.
* `POST /api/diagnose`
  * Dedicated disease classification pipeline.

### 3. Scan History
* `GET /api/scans?limit=50&offset=0`
  * Retrieve paginated history from SQLite database.
* `GET /api/scans/{scan_id}`
  * Fetch complete scan details and recommendations.
* `DELETE /api/scans/{scan_id}`
  * Delete a scan record.

### 4. AI Plant Doctor & Bookmarks
* `POST /api/chat`
  * Payload: `{ "message": "...", "scan_id": "...", "conversation_history": [...] }`
* `GET /api/plants`
  * Retrieve user bookmarked plants.
* `POST /api/plants`
  * Bookmark a plant with cultivation notes.
* `DELETE /api/plants/{plant_id}`
  * Delete a bookmarked plant.
