# Architecture & Flow

## System Diagram

```
                              ┌───────────────┐
                              │     User      │
                              └───────┬───────┘
                                      │ upload / view results
                              ┌───────▼───────┐
                              │  React Frontend│  (Home, Image,
                              │                │   Signature, History, About)
                              └───────┬───────┘
                                      │ REST (JSON + multipart)
                              ┌───────▼───────┐
                              │ FastAPI Backend│
                              │  /image        │
                              │ /signature     │
                              │ /report /history│
                              └───┬───┬───┬────┘
                    ┌─────────────┘   │   └─────────────┐
                    ▼                 ▼                 ▼
            ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
            │ Image Engine  │ │Signature Engine│
            │ ELA + CNN     │ │ Siamese Network│
            │ + Grad-CAM    │ │ (EfficientNetB3)│
            └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
                    │ heatmap +        │ similarity
                    │ verdict          │ score
                    └─────────────┬────┴──────────────┘
                                  ▼
                            ┌───────────────────────┐
                            │   Report Generator     │
                            │ (reportlab + Jinja2)   │
                            └───────────┬───────────┘
                                        ▼
                                ┌───────────────┐
                                │ PDF Forensic  │
                                │    Report     │
                                └───────────────┘
```

## Request Flow (single image example)

1. User uploads an image via the React `ImageDetection` page.
2. Frontend sends `POST /image` (multipart) to FastAPI.
3. `routers/image.py` hands the file to `services/image_service.py`.
4. Service layer calls `preprocessing/image_preprocessing.py` → generates the ELA image.
5. ELA image is passed to the trained CNN in `models/image_forgery/`.
6. Grad-CAM runs against the CNN's last conv layer → heatmap overlay saved to `reports/` or served inline.
7. Service layer packages `{prediction, confidence, forgery_type, heatmap_url}` and returns it.
8. Frontend renders the verdict, confidence bar, and heatmap overlay.
9. On "Download Report," backend renders a PDF via `reportlab`/Jinja2 template and returns it from `/report/{case_id}`.

The signature flow mirrors this with grayscale/Otsu preprocessing and a similarity-score response.

## Why this separation (routers → services → models)
- **Routers** only handle HTTP concerns (validation, status codes) — keeps them thin and testable with `httpx`.
- **Services** hold the actual business logic and are import-able directly in unit tests or the `inference/` CLI scripts, without booting FastAPI.
- **Models** are swappable — if Team A upgrades the image CNN mid-project, nothing in `routers/` or the frontend needs to change, only `services/image_service.py`'s model-loading call.

## Data flow for training (offline, not user-facing)
```
datasets/ → preprocessing/*.py → training/train_*.py → models/*/  (saved weights)
```
This path runs once per model iteration during development — it is separate from the live inference path above.
