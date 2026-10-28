# PlantSathi AI — Architecture & Technical Design

## 1. System Overview

PlantSathi AI is an end-to-end, production-oriented artificial intelligence platform for plant species identification and leaf disease diagnosis. The system decouples botanical species classification from pathology screening, executing two distinct inference tasks rather than relying on a generic LLM.

```
                          ┌──────────────────────────┐
                          │   React + Vite Frontend  │
                          │   (Tailwind CSS + TS)    │
                          └─────────────┬────────────┘
                                        │ HTTP / Multipart
                                        ▼
                          ┌──────────────────────────┐
                          │     FastAPI Gateway      │
                          │     (Uvicorn Engine)     │
                          └──────┬────────────┬──────┘
                                 │            │
            ┌────────────────────┘            └────────────────────┐
            ▼                                                      ▼
┌───────────────────────────┐                        ┌───────────────────────────┐
│ Plant Identification      │                        │ Disease Classification    │
│ Vision Transformer (ViT)  │                        │ MobileNetV2 (PlantVillage)│
│ umutbozdag/plant-identity │                        │ linkanjarad/mobilenet_v2  │
└───────────┬───────────────┘                        └─────────────┬─────────────┘
            │                                                      │
            └────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Confidence Evaluator   │
                    │  (Uncertainty Bands)    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Recommendation Engine  │
                    │  & AI Plant Doctor      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    SQLite Persistence   │
                    │  (SQLAlchemy Async ORM) │
                    └─────────────────────────┘
```

---

## 2. Machine Learning Pipelines

### A. Plant Species Identification
* **Model:** `umutbozdag/plant-identity` (Vision Transformer architecture)
* **Fallback:** `google/vit-base-patch16-224`
* **Task:** Multi-class botanical species classification.
* **Input:** RGB image, resized to 224×224, normalized using ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`.
* **Output:** Ranked candidates with softmax probability scores.

### B. Plant Disease Classification
* **Model:** `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`
* **Dataset:** PlantVillage (54,305 curated leaf images across 38 classes).
* **Supported Crops (14):** Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato.
* **Task:** Pathology classification distinguishing healthy foliage from specific fungal, bacterial, and viral infections.
* **Preprocessing:** Centered crop, resized to 224×224, pixel scaling to `[0, 1]`.

---

## 3. Uncertainty & Out-of-Distribution Policy

* **Crop Compatibility Gate:** If a plant is identified as a non-supported species (e.g. *Ficus elastica* or *Rosa chinensis*), the system marks the disease diagnosis as tentative with an explicit warning banner that the species is outside the 14 PlantVillage crops.
* **Confidence Bands:**
  * Score ≥ 0.80: High confidence.
  * Score 0.40–0.79: Medium confidence (advises visual corroboration).
  * Score < 0.40: Low/Insufficient confidence (prompts for clearer, closer leaf photography).

---

## 4. Database Schema (SQLite / SQLAlchemy Async)

* **`scan_records`:**
  * `id` (UUID PK)
  * `created_at`, `updated_at` (Timestamps with UTC timezone)
  * `plant_common_name`, `plant_scientific_name`, `plant_confidence`, `plant_confidence_level`
  * `disease_label`, `disease_crop`, `disease_name`, `disease_confidence`, `disease_status`
  * `warnings` (JSON array of strings)
  * `recommendations` (JSON array of care items)
  * `image_filename`, `image_stored`
  * `analysis_duration_ms`

* **`saved_plants`:**
  * `id` (UUID PK)
  * `created_at`
  * `common_name`, `scientific_name`
  * `notes`
  * `scan_id` (FK to scan_records)
