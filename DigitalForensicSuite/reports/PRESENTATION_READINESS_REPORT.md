# SecureVision-XAI — Presentation Readiness Report

**Project:** SecureVision-XAI: An Explainable AI Framework for Signature Verification and Image Forgery Detection  
**Audit date:** 6 September 2026  
**Presentation date:** 19 September 2026  
**Basis:** Source-code review, included data/checkpoint inspection, direct checkpoint inference, API test run, frontend production build, and frontend lint run.

---

## 1. Executive summary

SecureVision-XAI has a strong and presentation-worthy **product concept**: one web application supports two related forensic tasks—offline signature verification and image-manipulation detection—and returns a numeric decision together with a visual explanation. The repository has a clean high-level separation between React user interface, FastAPI API, preprocessing, model definitions, training, and inference. The frontend compiles for production, and 26 of 31 automated checks pass.

However, it is currently a **prototype, not a reliable forensic system or an end-to-end ready demo**. The included data are very small samples, the saved signature model is ineffective at its deployed threshold, several advertised features are placeholders, and two integration defects prevent the main UI flows from working as shipped. These are normal late-project issues, but they must be handled honestly and in priority order before the presentation.

### Bottom-line assessment

| Area | Status | Evidence-based assessment |
|---|---:|---|
| Product concept and UI design | Green | Clear dual-module problem/solution; responsive-looking React UI builds successfully. |
| Image pipeline implementation | Amber | ELA → EfficientNet-B0 → Grad-CAM is implemented and a checkpoint loads, but model evidence is insufficient for a real-world claim. |
| Signature pipeline implementation | Red | Siamese ResNet18 pipeline exists, but the current 0.5 threshold labels every included evaluation pair as genuine. |
| Backend/API integration | Red | File paths resolve one directory too high; valid API tests fail before inference. |
| Frontend-to-signature API integration | Red | UI sends `query`; API requires `questioned`, producing validation failure. |
| Video, history, PDF reports | Not implemented | Routes/files are scaffolded or placeholders and should not be demonstrated as working. |
| Test engineering | Amber | Good smoke/contract coverage, but it validates untrained models and currently ends at 26 passed / 5 failed. |
| Presentation readiness today | Amber/Red | Present the architecture and prototype progress; do not make accuracy, court-readiness, localization, report-download, video, or history claims until fixed and evidenced. |

**Recommended presentation framing:** “SecureVision-XAI is a dual-module explainable-AI prototype. We have implemented the end-to-end model pipelines and user interface; the remaining work is robust model validation and final API integration.” This is credible, technically accurate, and still highlights meaningful engineering.

---

## 2. What the project is trying to solve

Digital documents are routinely used in banking, education, legal services, and e-governance. Two common integrity questions are:

1. Does a questioned handwritten signature match a trusted reference signature?
2. Has a digital image been manipulated, for example by splicing or copy-move editing?

Many existing tools address only one question and produce an unexplained label. SecureVision-XAI proposes a combined web system that provides an outcome, score, and Grad-CAM visualisation rather than a black-box result alone.

### Project objectives

- Build an image-forgery classifier using Error Level Analysis (ELA) and EfficientNet-B0.
- Build an offline signature-verification model using a Siamese ResNet18 and cosine similarity.
- Expose both capabilities through a FastAPI REST API.
- Provide a simple React upload UI and show Grad-CAM heatmaps.
- Eventually add analysis history and downloadable reports.

The first four objectives are substantially represented in the codebase. The last objective is only planned at this snapshot.

---

## 3. Actual system architecture

```text
                         Browser / React + Vite
                                      |
               multipart upload + JSON response over HTTP
                                      |
                              FastAPI backend
                       /image/       /signature/
                          |                |
                 image service    signature service
                          |                |
          ELA preprocessing      Otsu + morphology cleaning
                          |                |
              EfficientNet-B0       Siamese ResNet18
                          |                |
            class probabilities    cosine similarity
                          |                |
                       Grad-CAM visual explanation
                                      |
                         result rendered in React
```

### Architectural strengths

- **Separation of concerns:** routers receive HTTP requests, services manage uploads/model loading, and inference/preprocessing modules can also run from the command line.
- **Lazy loading:** models are intended to load once on first use rather than on every request.
- **Typed result contracts:** Pydantic schemas define the image and signature response fields.
- **User-centred outputs:** verdicts, probabilities/similarity, latency, and image heatmaps are all designed for a practical UI.
- **Traceable project layout:** datasets, preprocessing, training, models, inference, backend, frontend, and tests have dedicated directories.

### Implemented versus planned scope

| Capability | Code status | UI status | Safe presentation statement |
|---|---|---|---|
| Image forgery analysis | Implemented prototype | Implemented page | “Implemented pipeline; validation is ongoing.” |
| Signature verification | Implemented prototype | Implemented page | “Implemented pipeline; model recalibration/retraining is required.” |
| Grad-CAM output | Implemented for both | Toggle exists | “Visual attention aid; not yet validated as pixel-accurate localization.” |
| Video deepfake analysis | `NotImplementedError` | Placeholder | “Planned future extension.” |
| Analysis history | `NotImplementedError` | Placeholder | “Planned future extension.” |
| PDF forensic report | `NotImplementedError` | No active UI flow | “Planned future extension.” |
| Database / persistent cases | Dependency/docs only | No feature | “Not implemented in this snapshot.” |

---

## 4. Technical design, explained for a presentation

### 4.1 Image-forgery module

**Input:** JPEG, PNG, BMP, TIFF image.

**Preprocessing:** The system opens the image, saves an in-memory JPEG version at quality 95, calculates the pixel-wise difference between original and recompressed versions, and amplifies that difference 10×. This creates an ELA image. Compression inconsistencies can reveal editing traces, especially in JPEG-based images.

**Model:** An ImageNet-initialised EfficientNet-B0 backbone produces a 1,280-dimensional feature vector. A dropout layer and a two-class linear head return logits for `AUTHENTIC` and `FORGED`.

**Decision:** Softmax converts logits into `p_authentic` and `p_forged`; the code chooses `FORGED` where `p_forged >= 0.5`.

**Explanation:** Grad-CAM produces a heatmap over the original image. It is returned as base64-encoded PNG data and displayed on demand in the UI.

**Good way to describe it verbally:**

> “ELA makes compression differences visible to the model. EfficientNet learns a compact representation of those forensic artefacts, and Grad-CAM helps us inspect the regions that influenced the network.”

Do not say that ELA proves tampering or that the heatmap precisely identifies manipulated pixels. Both need localization validation against masks first.

### 4.2 Signature-verification module

**Input:** one known reference signature and one questioned signature.

**Preprocessing:** The images are converted to grayscale. Otsu thresholding separates ink-like strokes from background; morphological opening removes small noise and closing reconnects nearby strokes. The cleaned image is then represented as a 256 × 256 three-channel tensor normalised using ImageNet statistics.

**Model:** A Siamese network uses one shared ResNet18 encoder for both images. Each branch produces a 128-dimensional L2-normalised embedding. Training uses contrastive loss: genuine pairs should be close in embedding space, forged pairs should be separated by a margin.

**Decision:** The code computes cosine similarity, maps it into [0, 1], scales it to a percentage, and currently marks it `GENUINE` at or above 0.5.

**Good way to describe it verbally:**

> “Instead of learning a fixed class for every writer, the Siamese architecture learns a feature space where matching signatures are expected to be close and non-matching signatures farther apart.”

This architecture choice is well matched to pairwise verification, but its decision threshold must be chosen from validation data—not assumed to be 0.5.

---

## 5. Data, checkpoints, and measured results

### 5.1 What is actually included locally

| Local set | Count | Implication |
|---|---:|---|
| CASIA-style authentic image samples | 14 | A demo/training subset, not a full benchmark. |
| CASIA-style tampered image samples | 14 | A demo/training subset, not a full benchmark. |
| CEDAR-style genuine signature samples | 25 | Five writers × five samples locally. |
| CEDAR-style forged signature samples | 25 | Five writers × five samples locally. |

The supplied checkpoint metadata show:

| Checkpoint | Saved epoch | Stored metric |
|---|---:|---|
| `best_efficientnet.pth` | 3 | AUC 1.0000; accuracy 1.0000 |
| `best_siamese.pth` | 2 | AUC 0.5000; EER 0.3750 |

The values are recorded by the scripts, but they were obtained from extremely small validation partitions: five image samples and seven signature pairs. They are not suitable headline performance claims.

### 5.2 Reproducible audit evaluation

The repository’s deterministic split logic creates 28 image samples (23 train / 5 validation) and 35 signature pairs (28 train / 7 validation). It is not stratified by writer or source and does not provide a held-out test set.

I directly loaded the supplied checkpoints and evaluated them across all included labelled samples/pairs. This is **not an unbiased test**—some samples may have contributed to training—but it is a useful sanity check.

| Module | Result on all included data | What it means |
|---|---|---|
| Image forgery | 23/28 correct (82.14%); ROC-AUC 1.0000; confusion matrix `[[14, 0], [5, 9]]` where rows are actual `[authentic, forged]` and columns are predicted `[authentic, forged]` | The model correctly called all 14 authentic samples but missed 5 of 14 forged samples. Score ranking can be good while the fixed 0.5 threshold still misses positives. |
| Signature verification | 10/35 correct (28.57%); ROC-AUC 0.4400; confusion matrix `[[10, 0], [25, 0]]` where positive is forged | At the deployed threshold, every pair was labelled genuine. This checkpoint/threshold must not be used for a signature-forgery claim. |

Two direct spot checks reinforce the same conclusion:

- A labelled tampered image (`Tp_sample_1.jpg`) was returned as **AUTHENTIC** with 52.9% confidence.
- A labelled forged signature was returned as **GENUINE** with 98.7% similarity/confidence.

### 5.3 How to report metrics responsibly

For the presentation, do **not** display “100% accuracy” or “AUC 1.0” without the sample size and split procedure. The correct wording today is:

> “The prototype has completed early training runs on a small local subset. We have identified threshold calibration and generalisation as the next validation tasks.”

For a defensible final result, train on the full permitted datasets, maintain a separate untouched test set, and report:

- **Image module:** accuracy, precision, recall, F1, ROC-AUC, confusion matrix, and per-forgery-type results.
- **Signature module:** FAR, FRR, EER, ROC-AUC, threshold selected on validation data, and writer-disjoint test performance.
- **Explainability:** only claim localisation after comparing heatmaps to CASIA masks using an appropriate localization metric such as IoU.

---

## 6. Validation performed during this audit

| Check | Outcome | Notes |
|---|---|---|
| Backend pytest suite | 26 passed / 5 failed | All preprocessing, model-shape, inference-smoke, health, and missing-file validation tests passed. Valid upload-path tests failed. |
| Direct checkpoint inference | Runs | Both supplied checkpoints loaded and generated decisions plus base64 heatmaps when called directly with correct local paths. |
| Frontend production build | Passed | Vite produced production assets successfully. |
| Frontend lint | Passed with 7 warnings | Warnings are unused imports/constant; cleanup is recommended but does not prevent build. |

### Important test limitation

The API tests deliberately substitute random/untrained models. They prove output shape and endpoint wiring under a mocked model; they do **not** validate the real checkpoint’s forensic performance. Add a small controlled integration suite using the actual trained models before presenting model quality.

---

## 7. Findings and priority fixes

### Must fix before demonstrating the two implemented modules

| Priority | Finding | Impact | Location | Recommended remediation |
|---:|---|---|---|---|
| P0 | Backend project root is calculated one level too high. Uploads resolve to `.../Projects/uploads`, outside this repository; model paths resolve similarly. | Valid `/image/` and `/signature/` API upload tests return HTTP 500. In a normal environment the wrong model path can silently fall back to an untrained model. | `backend/app/services/image_service.py`; `backend/app/services/signature_service.py` | Resolve the project root as `Path(__file__).resolve().parents[3]`, then test model/upload paths explicitly. Prefer absolute paths derived from that root. |
| P0 | Signature web client sends `query`; API expects `questioned`. | The signature page receives HTTP 422 even if the backend path issue is fixed. | `frontend/src/api/client.js`; `backend/app/routers/signature.py` | Send `form.append('questioned', query)` or rename both sides consistently. Add an end-to-end test for the browser contract. |
| P0 | Signature decision threshold is unusable for current weights. | All 35 included pairs were labelled genuine. A forged signature can be falsely accepted with high apparent confidence. | `inference/predict_signature.py` | Retrain with adequate data; choose and store a validation-derived threshold; reject release if FAR/FRR/EER are unacceptable. |
| P0 | Image model is not adequately validated. | Five of 14 included forged samples were missed. The local data are too small to claim general performance. | dataset/training/checkpoint process | Train/evaluate with a full, documented split and calibrated threshold; present metrics with sample counts. |
| P0 | The UI/docs imply features that do not exist: PDF reports, history, and video analysis. | An examiner can click them or ask for the advertised report. | `frontend/src/App.jsx`; `backend/app/routers/report.py`; video files | Either implement them fully or label/remove them as “Future work” for the demo. Do not show “court-ready reports.” |

### Important quality and credibility fixes

| Priority | Finding | Why it matters | Recommendation |
|---:|---|---|---|
| P1 | Image Grad-CAM is always targeted to the forged class, even when verdict is authentic. | The display does not necessarily explain the returned verdict. | Target the predicted class and label the visualization accordingly. |
| P1 | Signature Grad-CAM wrapper scores the sum of a single embedding, not the reference–questioned similarity. | The heatmap does not faithfully explain the pairwise decision. | Implement an explanation objective based on pair similarity/distance, or describe it only as a preliminary visual attention map. |
| P1 | Training split is by pairs, not writers; data can leak across train/validation. | Results may overestimate ability to handle unseen writers. | Use writer-disjoint train/validation/test partitions for signatures. |
| P1 | Signature pairs are imbalanced: 25 forged vs 10 genuine in the local set. | Accuracy alone becomes misleading. | Balance pair construction or use weighted sampling; report FAR, FRR and EER. |
| P1 | `torch.load` uses an unsafe default warning. | Loading unknown checkpoints may execute pickle data. | Use `weights_only=True` once checkpoint metadata are made compatible, and only load trusted checkpoint sources. |
| P1 | Input validation is based on filename extension and reads the entire upload before the size check. | Invalid content and memory pressure are insufficiently controlled. | Validate image decoding/mime content and stream or enforce size before fully buffering. |
| P1 | Backend allows all CORS origins and returns raw exception details. | Appropriate for a local demo, unsafe in deployment. | Configure explicit frontend origin and log detailed errors server-side only. |
| P1 | Documentation conflicts on scope/architecture. | An examiner may notice model and feature contradictions. | Make README, architecture diagram, UI About page, and slides describe the same two implemented modules. |
| P2 | Seven frontend lint warnings for unused symbols. | Minor polish issue. | Remove unused imports and `PAGES` constant. |
| P2 | Default Vite favicon and generic page title remain. | Reduces product polish during demo. | Use the supplied product icon and set title to SecureVision-XAI. |
| P2 | Pytest emits an asyncio configuration deprecation warning. | Not a functional issue but avoidable technical noise. | Explicitly set the default asyncio fixture-loop scope in `pytest.ini`. |

---

## 8. Documentation consistency audit

The repository currently mixes an **older three-module roadmap** with the **actual two-module implementation**.

| Source | Accurate portions | Needs correction before slides/demo |
|---|---|---|
| `README.md` | Describes the current dual image/signature concept and correct model families. | Remove/qualify downloadable reports and unverified capability claims. |
| `docs/ARCHITECTURE.md` | Useful layer separation explanation. | Shows video engine, history, PDF generator, and EfficientNet-B3 signature engine, none of which match current implementation. |
| `docs/TECH_STACK.md` | Captures intended ecosystem. | Describes video model, database/report deployment plans, and EfficientNet-B3 signature details that are not implemented. |
| `docs/ROADMAP.md` | Suitable as historical planning document. | Keep clearly marked “roadmap”; do not present future phases as delivered. |
| Frontend home/About pages | Attractive visual summary of the core problem. | Calls reports “court-ready,” calls models trained on full named datasets, and exposes future pages. Qualify these claims. |

**Recommended single source of truth for the presentation:** the README revised to say “two-module prototype; image and signature flows in implementation; video/history/PDF planned.” Make every slide use the same wording.

---

## 9. A realistic plan from 6 September to 19 September

### 6–8 September: make an honest, demonstrable vertical slice

1. Fix the backend root path in both services.
2. Fix the `query`/`questioned` frontend API mismatch.
3. Make missing checkpoints fail clearly with HTTP 503; never silently infer with untrained weights.
4. Run `pytest tests -v` again until all 31 tests pass.
5. Keep only Image and Signature active in navigation. Label Video, History, and PDF Reports as “Future work,” or hide them temporarily.
6. Capture one controlled image demo and one controlled signature demo only after verifying the real model response.

### 9–13 September: establish trustworthy model evidence

1. Obtain/use the full permitted training data rather than only local examples.
2. Create reproducible train/validation/test splits. For signature verification, keep writers disjoint across splits.
3. Retrain and save the preprocessing settings, split seed, threshold, and metrics with every checkpoint.
4. Select the signature threshold from validation EER/operating point—not a hard-coded 0.5.
5. Produce one metrics table and one confusion matrix per model using the untouched test partition.
6. Calibrate the image threshold based on the desired false-negative versus false-positive trade-off.

### 14–16 September: improve explanation and demo reliability

1. Make image Grad-CAM target the predicted class.
2. Either repair signature pairwise explainability or label it as exploratory.
3. Add an actual-model integration test with two known demo samples per module.
4. Clean UI text, favicon, title, lint warnings, and documentation inconsistencies.
5. Prepare screenshots/recording as a contingency for environment or inference delays.

### 17–18 September: rehearse

1. Run the demo on the exact laptop/network you will use.
2. Verify backend start, frontend start, model checkpoint location, upload permissions, and the two selected files.
3. Rehearse a 7–10 minute talk twice, including answers to limitations questions.
4. Keep a static screenshot of results and metrics in the slides as a fallback.

### 19 September: presentation rule

Demonstrate only the flows that passed on the presentation machine. If model retraining is incomplete, present the system as an implemented **prototype architecture with preliminary results**, not as deployable forensic evidence.

---

## 10. Suggested presentation structure (8–10 minutes)

| Slide | Time | Key message | Recommended visual |
|---:|---:|---|
| 1. Title | 0:30 | SecureVision-XAI makes document authenticity analysis more explainable. | Product title and two-module graphic. |
| 2. Problem | 0:45 | Forged signatures and manipulated images are costly; black-box outputs reduce trust. | Two simple examples: signature and edited image. |
| 3. Proposed solution | 0:45 | One modular application combines verification and forgery detection with visual explanations. | Simplified architecture diagram from section 3. |
| 4. Image module | 1:00 | ELA exposes compression artefacts; EfficientNet classifies; Grad-CAM aids inspection. | ELA/input/heatmap pipeline graphic. |
| 5. Signature module | 1:00 | Siamese learning compares a reference and questioned signature in embedding space. | Two input signatures → shared encoder → similarity score. |
| 6. Application workflow | 1:00 | User uploads, API processes, UI renders verdict and explanation. | Screenshot or controlled live demo. |
| 7. Engineering contribution | 0:45 | React + FastAPI + PyTorch, modular services, typed APIs, tests. | Tech stack and project layout. |
| 8. Preliminary results and validation method | 1:15 | Explain exactly which dataset split and metrics are available; do not overstate. | Compact metrics table with sample counts. |
| 9. Limitations and future work | 0:45 | Robust validation, calibrated thresholds, real pairwise XAI, reports/history/video are next. | Three-item roadmap. |
| 10. Conclusion | 0:30 | The contribution is an explainable dual-module forensic prototype with a clear route to validation. | One-sentence takeaway. |

### Suggested opening (about 30 seconds)

> “Good morning. Our project is SecureVision-XAI, an explainable AI prototype for two document-forensics tasks: detecting image manipulation and comparing handwritten signatures. Rather than returning only a label, our system combines a prediction score with a visual explanation so that a human reviewer can understand what the network considered important.”

### Suggested closing (about 20 seconds)

> “SecureVision-XAI demonstrates a modular dual-model workflow from upload to explainable result. Our next focus is rigorous dataset-scale validation, calibrated operating thresholds, and converting the prototype into a dependable decision-support tool.”

---

## 11. Expected questions and strong answers

| Likely question | Safe, technically strong answer |
|---|---|
| Why use a Siamese network instead of ordinary classification? | “Verification is inherently pairwise. A Siamese network learns an embedding in which a reference and questioned signature can be compared, which is more suitable for unseen identities than one fixed class per signer.” |
| Why ELA? | “Recompression can expose local compression inconsistencies introduced by editing. It is a useful forensic cue, not conclusive proof, so we combine it with a learned classifier and human review.” |
| What does Grad-CAM provide? | “It shows regions that influenced the model’s score. It improves inspectability, but it is not a guarantee of causal or pixel-perfect tamper localisation.” |
| Can it be used in court today? | “No. It is a decision-support prototype. Court use would require data governance, calibration, independent validation, chain of custody, security controls, and expert human review.” |
| What are your accuracy results? | “We have preliminary runs on a small local subset, so we do not treat them as deployment accuracy. We are reporting sample counts and are moving to a held-out, dataset-scale test protocol.” |
| Why did you choose FastAPI and React? | “FastAPI gives typed API contracts and automatic documentation; React gives a clear upload-and-result experience. The separation lets us update a model without rewriting the interface.” |
| What is the main limitation? | “Model generalisation. Compression style, editing tools, image source, and writer variation can change the input distribution, so rigorous split design and calibration are essential.” |
| What is next? | “Complete validated training/testing, select operating thresholds from validation data, strengthen pairwise explainability, then add case history and reporting.” |

---

## 12. Final presentation checklist

- [ ] UI-to-API image upload returns a real response using the correct checkpoint.
- [ ] UI-to-API signature upload uses `questioned` and returns a real response.
- [ ] Full test command reports **31 passed** with no failed API tests.
- [ ] Two verified demo files and their expected outputs are prepared locally.
- [ ] Results slide includes dataset size, split strategy, and metric definitions.
- [ ] No slide says “court-ready,” “100% accurate,” “localizes tampering,” or “trained on full dataset” unless evidence exists.
- [ ] Video, history, and PDF report functionality is either working or explicitly labelled future work.
- [ ] README, architecture diagram, UI About page, and slides agree on a two-module scope.
- [ ] A recorded demo or screenshots are embedded as a fallback.
- [ ] Each presenter knows the limitations answer and can state it confidently.

---

## 13. Audit conclusion

This project has the right problem selection, a coherent dual-module architecture, thoughtfully separated code, a polished frontend direction, and the foundations for explainable outputs. Those are substantial strengths for a presentation.

The immediate priority is to turn the current implementation into a **truthful, repeatable vertical slice**: repair API integration, stop silent fallback to untrained weights, avoid advertising unimplemented modules, and establish evidence for the trained models. The signature classifier in particular requires retraining and threshold calibration before it can be demonstrated as verification. With that discipline, the presentation can be compelling precisely because it is transparent about both the innovation and the engineering path remaining.
