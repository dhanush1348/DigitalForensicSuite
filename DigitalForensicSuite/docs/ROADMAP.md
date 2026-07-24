# 6-Week Roadmap (Team of 4)

The original plan assumed 12 weeks solo. Compressed to 6 weeks by **parallelizing the three engines across teammates** instead of building them sequentially. Suggested role split — adjust to actual skills/interests:

- **Dev A — Image Engine + Explainability** (Modules 1 & 7 for images)
- **Dev B — Video Engine** (Module 2)
- **Dev C — Signature Engine** (Module 3)
- **Dev D — Backend/API + Frontend + Report Generator** (Phases 5, 6, 8) — integrates whatever A/B/C produce

All four collaborate on Phase 1 (research) and Phase 9 (testing) together.

| Week | Everyone | Dev A (Image) | Dev B (Video) | Dev C (Signature) | Dev D (Backend/Frontend) |
|---|---|---|---|---|---|
| **1** | Literature review together (1–2 days); repo scaffolding (done ✅); submit FaceForensics++/DFDC access requests **today** — this is the biggest schedule risk | Download/verify CASIA v2 | Download/verify video datasets (pending access) | Download/verify CEDAR/BHSig260/GPDS960 | Scaffold FastAPI skeleton (done ✅) + React skeleton; define API contracts (request/response shapes) so A/B/C can build against a spec before the real models exist |
| **2** | Mid-project sync: confirm API contracts still match | Build ELA preprocessing + CNN architecture; start training | Build frame extraction + face alignment pipeline | Build signature binarization pipeline + Siamese network architecture | Build React pages (upload UI, mock data first) against the agreed API contract |
| **3** | | Train/tune image CNN; integrate Grad-CAM | Build CNN+Bi-LSTM; start training (this is your longest training job — start it early and iterate while it runs) | Train Siamese network; compute FAR/FRR/EER on val set | Wire up `/image` and `/signature` endpoints to real (even if early/rough) models as they become available |
| **4** | | Finalize image model + heatmap output; write image unit/integration tests | Continue training/tuning; integrate frame-level Grad-CAM + timeline | Finalize signature model; write unit/integration tests | Wire up `/video` endpoint; build History page + report download UI |
| **5** | Full integration week — all four in the same room/call | Support integration bugs in image pipeline | Support integration bugs in video pipeline (likely the trickiest — buffer time here) | Support integration bugs in signature pipeline | Build PDF Report Generator (Phase 8); wire all three engines end-to-end |
| **6** | End-to-end testing (Phase 9) together; fix cross-cutting bugs; polish demo; prep presentation/documentation | | | | Deploy (Docker + Render/Railway + Vercel per `TECH_STACK.md`) |

## Critical path / risks
1. **Dataset access requests (video)** — FaceForensics++/DFDC often take days for approval. If this isn't submitted Day 1, Dev B's whole track slips and compresses everyone else's integration week.
2. **API contract drift** — since Dev D builds the frontend/backend against a *spec* before A/B/C's models exist, freeze the request/response shapes in Week 1 and only change them with a quick team sync, not silently.
3. **Video model training time** — Bi-LSTM/3D CNN training on deepfake datasets is the slowest job in the whole project. Start it as early as Week 2–3 even with a partial dataset, and keep iterating rather than waiting for a "final" dataset first.
4. **Integration week (Week 5) is the real crunch** — budget it as a full week, not a formality, since this is where three independently-built engines meet one backend for the first time.

## Definition of "demo ready" (end of Week 6)
- [ ] All three detection flows work end-to-end through the actual UI (not just Postman/curl)
- [ ] Each engine reports a real metric on its held-out test set (not just "it runs")
- [ ] PDF report generates correctly for at least one real case per engine
- [ ] Known limitations documented (e.g., "video model trained on N hours due to time constraints") — an honest limitations section reads far better in a final-year evaluation than silence
