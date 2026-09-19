# SecureVision-XAI: An Explainable AI Framework for Signature Verification and Image Forgery Detection

**Department of Information Technology**  
**S R K R Engineering College (A), Bhimavaram - 534204**  
*4/4 B.Tech (IT / AI&DS / CSBS) 2nd Semester (R23) AY-2026-2027*

---

## Abstract
The increasing use of digital documents in banking, legal services, education, and e-governance has made document authentication a critical challenge. SecureVision-XAI is a dual-module prototype for offline signature verification and digital image forensics. Its main research goal is to move beyond a binary “forged” label by combining classification, suspicious-region localization, and supporting forensic evidence into a human-readable explanation.

The current implementation contains the first prototype of both modules. The image path uses ELA and EfficientNet-B0 for authentic-versus-tampered classification and Grad-CAM for model attribution. The planned complete system adds manipulation-type classification, mask-based localization, feature matching, noise/compression analysis, and evidence-based explanations. Grad-CAM is treated as an attribution aid, not as proof of tampering.

---

## Problem Statement
The rapid digitization of documents has increased the risk of forged signatures and manipulated digital images. Existing verification systems generally focus on only one problem — either signature verification or image forgery detection — and often behave as "black-box" models without explaining their predictions. This lack of transparency limits their adoption in sensitive domains such as banking, legal documentation, and forensic investigations. There is a need for an integrated AI-based framework that independently performs signature verification and image forgery detection while providing interpretable explanations for every prediction.

---

## System Architecture

```
                       SecureVision-XAI
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
     SIGNATURE MODULE                        IMAGE MODULE
          │                                       │
  CEDAR / BHSig260                        CASIA v2.0 / IMD2020
          │                                       │
  Siamese ResNet18                        EfficientNet-B0 + ELA
          │                                       │
  Genuine / Forged                        Real / Forged
          │                                       │
          └───────────────────┬───────────────────┘
                              ▼
                  Mask + Evidence + Grad-CAM
                              │
                 Human-readable explanation
                              │
                    FastAPI REST Backend
                              │
                     React / Vite Web UI
```

---

## Key Modules

### Module 1: Signature Verification
- **Backbone**: Siamese Neural Network with shared ResNet18 encoder & L2-normalized 128-d embedding head.
- **Preprocessing**: Grayscale → Otsu binarization → morphological cleaning → resize (256x256) → ImageNet normalization.
- **Similarity Metric**: Cosine similarity score (0–100%) & contrastive loss during training.
- **XAI**: Grad-CAM visual heatmap overlay on pen-stroke regions.
- **Primary Dataset**: CEDAR Signature Dataset (55 signers, 24 genuine & 24 forged per writer).

### Module 2: Image Forgery Detection
- **Backbone**: EfficientNet-B0 binary classifier with ELA preprocessing pipeline.
- **Preprocessing**: Error Level Analysis (re-compressed JPEG at Q=95, 10x pixel diff amplification) → resize (224x224).
- **Current output**: Authentic/forged probabilities and a Grad-CAM attribution heatmap.
- **Planned output**: Copy-move/splicing/type prediction, predicted tampering mask, forensic indicators, and explanation.
- **Primary dataset target**: CASIA v2.0 with corrected groundtruth masks; DEFACTO and CoMoFoD are candidates for broader type and localization coverage.

## What counts as an explanation?

The system will separate three kinds of output:

1. **Model decision**: probability that the image is authentic or forged.
2. **Model attribution**: regions that influenced the neural network, such as Grad-CAM.
3. **Forensic evidence**: measured indicators such as duplicated local features, compression inconsistency, noise differences, or unusual boundaries.

The final explanation must be traceable to measured outputs. For example:

> “Potential copy-move manipulation. Similar local features were found in two spatially separated regions. The segmentation model marked the highlighted pixels as suspicious. This is an indicator, not conclusive proof.”

## Current status and limitations

- The local image subset contains 28 CASIA-style images: 14 authentic and 14 tampered.
- No ground-truth mask directory or manipulation-type manifest is currently present locally.
- The existing image checkpoint was trained on a very small split and is not evidence of production accuracy.
- The signature verifier is a secondary prototype; its current checkpoint requires retraining and threshold calibration.
- Video analysis, history, and report routes are not complete implementations.
- The full staged plan is in [docs/ROADMAP.md](docs/ROADMAP.md).

Training Stage 1 on the current subset is useful only as a smoke test. Full localization and evidence training must wait for a permitted dataset with masks and labels.

---

## Benchmark Datasets & Source Links

- **Handwritten Signature Datasets (CEDAR & BHSig260)**:  
  [https://www.kaggle.com/datasets/ishanikathuria/handwritten-signature-datasets](https://www.kaggle.com/datasets/ishanikathuria/handwritten-signature-datasets)
- **CASIA v2.0 Corrected Groundtruth**:  
  [https://github.com/SunnyHaze/CASIA2.0-Corrected-Groundtruth](https://github.com/SunnyHaze/CASIA2.0-Corrected-Groundtruth)
- **DEFACTO**: candidate source for multiple manipulation types and masks; verify its license and access terms before use.
- **CoMoFoD**: candidate source for copy-move detection and localization; verify its license and access terms before use.

Keep external datasets in separate directories and create a unified manifest with `image_path,type,mask_path,source,group_id,split`. Split by source/original-image group to prevent related derivatives from crossing train, validation, and test sets.


---

## Tech Stack

- **Frontend**: React 19, Vite, Vanilla CSS Design System (Dark mode, glassmorphism), Lucide icons
- **Backend**: FastAPI, Uvicorn, Pydantic v2, Pydantic Settings, Async HTTPX & Aiofiles
- **Deep Learning & Computer Vision**: PyTorch 2.4, Torchvision, `timm`, OpenCV, Pillow, `pytorch-grad-cam`
- **Testing**: pytest, pytest-asyncio (31 tests passed)

---

## Quick Start

### 1. Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Development Server
```bash
cd frontend
npm run dev
```

### 3. Run Automated Test Suite
```bash
pytest tests/ -v
```

### 4. Run the existing image training smoke test

```bash
python training/train_image.py --data-dir datasets/images/CASIA2 --cpu-debug --epochs 2 --batch-size 4
```

This uses a tiny local subset and is only a pipeline check. It must not be reported as the final model evaluation.

### 5. Build the current local manifest

```bash
python datasets/build_manifest.py
```

This writes `datasets/manifests/image_manifest.csv`. The current subset is recorded as 14 authentic and 14 `unknown_forgery` images with `unassigned` splits. Forgery types, masks, and source-disjoint splits must be filled from a larger labelled dataset before research training.

---

## Repository Layout

```
DigitalForensicSuite/
├── frontend/           # React app (ImagePage, SignaturePage, AboutPage, client.js)
├── backend/            # FastAPI app (routers, services, schemas, core config)
├── models/             # PyTorch model definitions & trained checkpoints (siamese, efficientnet)
├── datasets/           # Raw datasets & download guides (download_cedar.md, download_casia.md)
├── preprocessing/      # ELA generation, Otsu signature binarization, dataset builders
├── training/           # Training scripts (train_signature.py, train_image.py)
├── inference/          # Prediction + Grad-CAM heatmap scripts (predict_signature.py, predict_image.py)
├── reports/            # PDF forensic report generation
└── tests/              # Pytest test suite (test_preprocessing, test_inference, test_api)
```

---

## References

1. **Yoldar, M. T., Eryiğit, R., & Cantürk, N. (2025).** *Explainable AI in Signature Forgery Detection.* Pattern Recognition Letters, Elsevier, Vol. 198, pp. 93–100. DOI: 10.1016/j.patrec.2025.10.003
2. **Stergiou, K., Ougiaroglou, S., & Sidiropoulos, A. (2025).** *Signature Forgery Detection Using Deep and Machine Learning.* International Journal of Reliable and Quality E-Healthcare (SAGE). DOI: 10.1177/18724981251330068
3. **Xu, Z., Zhang, X., Li, R., Tang, Z., Huang, Q., & Zhang, J. (2025).** *FakeShield: Explainable Image Forgery Detection and Localization via Multi-modal Large Language Models.* ICLR 2025.
4. **Wu, X., Chen, X., Wu, X., Li, D., Chen, Z., He, Y., & Zhao, C. (2025).** *Explainable Image-Centric Forgery Detection: A Survey.* SSRN Preprint.
5. **Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017).** *Grad-CAM: Visual Explanations from Deep Networks via Gradient-Based Localization.* IEEE ICCV 2017. DOI: 10.1109/ICCV.2017.74
