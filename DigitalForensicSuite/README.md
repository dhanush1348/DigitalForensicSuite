# Digital Forensic Suite

Multi-modal deep learning system for detecting image manipulation, deepfake video, and signature forgery — with explainable visualizations and downloadable forensic reports.

## Team & Timeline
- **Team size:** 4
- **Duration:** 6 weeks
- **Roadmap:** see [`docs/ROADMAP.md`](docs/ROADMAP.md) for the week-by-week plan and role split
- **Architecture:** see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Tech stack + alternatives:** see [`docs/TECH_STACK.md`](docs/TECH_STACK.md)

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r ../requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Repository Layout

```
DigitalForensicSuite/
├── frontend/           # React app (upload UI, results, history, report download)
├── backend/            # FastAPI app (routers, services, schemas)
├── models/             # Trained model weights per engine (image_forgery, video_forgery, signature)
├── datasets/            # Raw datasets (gitignored — see docs/TECH_STACK.md for sources)
├── preprocessing/       # ELA, frame extraction, signature binarization scripts
├── training/            # Training scripts per model
├── inference/           # Inference/prediction scripts per model
├── reports/             # Generated PDF forensic reports (gitignored)
├── uploads/             # User-uploaded files at runtime (gitignored)
├── tests/               # backend/, models/, frontend/ test suites
└── docs/                # Architecture, tech stack, roadmap, testing strategy
```

## Status
🚧 Project scaffolded — Week 1 in progress (see ROADMAP.md).
