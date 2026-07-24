# Tech Stack — Where, How, and Alternatives

Each row: what it's for, where in the repo it's used, why it was picked, and what you could swap in instead if a teammate is more comfortable with something else or you hit a blocker.

## Frontend

| Tech | Used in | How | Alternatives |
|---|---|---|---|
| **React** | `frontend/src/` | Pages for Home, Image/Video/Signature detection, History, About; component state for upload previews, prediction results, heatmap overlays | **Streamlit** — much faster to build with (pure Python, no separate frontend team needed), but less polished/customizable UI and harder to make it look like a "real product" for a final demo. **Vue** — similar tradeoffs to React, smaller learning curve, less ecosystem support |
| **Axios / fetch** | `frontend/src/api/` | Calls the FastAPI endpoints (`/image`, `/video`, `/signature`, `/report`) | Native `fetch` (no extra dependency) works fine at this scale — Axios mainly helps if you want interceptors for auth later |
| **Chart/timeline lib** (e.g. `recharts`) | Video Detection page | Rendering the suspicious-frame timeline | Plain `<canvas>` or SVG if you want to avoid the dependency |

## Backend

| Tech | Used in | How | Alternatives |
|---|---|---|---|
| **FastAPI** | `backend/app/` | REST API: routers per engine, automatic OpenAPI docs at `/docs` (very useful so frontend devs can test endpoints without waiting on backend devs) | **Flask** — simpler mental model, no async/Pydantic learning curve, but no free interactive API docs and manual request validation. **Django REST Framework** — overkill for this scope |
| **Pydantic** | `backend/app/schemas/` | Request/response validation (e.g., rejecting non-image uploads before they hit the model) | Manual `if`/`else` validation — more error-prone, not recommended given deadline pressure |
| **SQLAlchemy + SQLite** | `backend/app/core/` (history/report metadata) | Store case ID, timestamp, prediction, confidence for the History page | Skip a DB entirely and just store JSON files per case in `reports/` — genuinely fine for a 4-person, 6-week project and removes a whole dependency to debug |

## Deep Learning / Computer Vision

| Tech | Used in | How | Alternatives |
|---|---|---|---|
| **PyTorch** | `models/`, `training/`, `inference/` | All three model architectures (image CNN, video CNN+Bi-LSTM, Siamese network) | **TensorFlow/Keras** — equally valid, Keras is arguably faster to prototype a Sequential CNN in. Pick based on what most of your 4 teammates already know — don't split the team across both |
| **timm** | Signature Siamese branches, optionally image CNN backbone | Pretrained EfficientNetB3 for feature extraction (transfer learning beats training from scratch given your dataset sizes and 6-week deadline) | Train a smaller custom CNN from scratch if compute is limited — MobileNetV2 (also mentioned in your original plan) is a lighter pretrained alternative to EfficientNetB3 |
| **OpenCV** | `preprocessing/*.py` | ELA generation (JPEG resave + diff), Otsu thresholding for signatures, general resize/color-space conversion | Pillow can handle basic resize/JPEG resave if you want one less dependency, but OpenCV's thresholding/morphology functions are genuinely better for the signature pipeline |
| **face-recognition / mediapipe** | `preprocessing/video_preprocessing.py` | Face detection + alignment before feeding frames to the video CNN | `face-recognition` (dlib-based) is more accurate but slower to install (dlib compilation issues are common — budget time for this or use mediapipe, which is pip-installable with no compiler needed) |
| **grad-cam (pytorch-grad-cam)** | Image + video services, for explainability (Phase 7) | Generates the heatmap overlay showing which pixels drove the "forged" prediction | Implement Grad-CAM manually (a few lines of hook code) if you want zero extra dependencies — the library just saves time |

## Reporting

| Tech | Used in | How | Alternatives |
|---|---|---|---|
| **reportlab + Jinja2** | Report Generator (Phase 8) | Renders the PDF forensic report (case ID, date, prediction, confidence, heatmap image, conclusion) | **WeasyPrint** — write the report as HTML/CSS and convert to PDF, often faster for a team more comfortable with web styling than reportlab's canvas API |

## Datasets (not code, but worth documenting sourcing here)

| Dataset | Used for | Notes |
|---|---|---|
| CASIA v2 | Image splicing/copy-move | Public, direct download, no access request needed |
| FaceForensics++ / DFDC / CelebDF | Deepfake video | **Require signed access agreements** — request access on Day 1, this is your biggest schedule risk |
| CEDAR / BHSig260 / GPDS960 | Signature verification | Public, direct download |

## Deployment (Phase 10 — only relevant once the demo is ready)

| Tech | Alternatives |
|---|---|
| Docker + Render/Railway (backend) | AWS EC2 if your team already has AWS credits/experience; otherwise Render/Railway are far less setup overhead for a 6-week deadline |
| Vercel (frontend) | Netlify — near-identical tradeoffs |
| SQLite → PostgreSQL | Stick with SQLite through the whole project if you never need concurrent writes — one less migration to manage before the deadline |
