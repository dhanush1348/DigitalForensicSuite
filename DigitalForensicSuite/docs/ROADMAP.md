# SecureVision-XAI Implementation Plan

## Project goal

Build an explainable image-forensics system that answers four questions:

1. Is the image authentic or potentially forged?
2. What manipulation type is most likely?
3. Which pixels or regions are suspicious?
4. What supporting evidence explains the decision?

The system must distinguish model attribution from forensic evidence. A Grad-CAM heatmap shows where a model looked; it does not, by itself, prove that those pixels were manipulated.

## Current baseline

| Area | Current state |
|---|---|
| Image classifier | EfficientNet-B0 prototype using ELA input |
| Image data | 28 local CASIA-style images: 14 authentic and 14 tampered |
| Image masks | Not present locally |
| Forgery-type labels | Not available in the current manifest |
| Signature verifier | Siamese ResNet18 prototype; secondary project module |
| Video analysis | Not implemented |
| Reports/history | Placeholder routes only |
| Automated tests | 31 tests passed at the last verification |

## Staged execution plan

### Stage 0 - Dataset acquisition and manifest

- Obtain a permitted dataset containing authentic images, forged images, manipulation types, and ground-truth masks.
- Keep CASIA, DEFACTO, and CoMoFoD in separate source directories.
- Create a common manifest with:

```text
image_path,type,mask_path,source,group_id,split
```

- Use source or original-image groups for splitting. Related derivatives must never cross train, validation, and test sets.
- **Gate:** do not start localization training until mask coverage and label quality are measured.

### Stage 1 - Binary forgery detection

- Train the existing EfficientNet-B0 pipeline on authentic versus forged images.
- Preserve ELA as an auxiliary forensic view, not as proof of manipulation.
- Report accuracy, precision, recall, F1, ROC-AUC, and a confusion matrix on an untouched test set.
- **Exit criterion:** both classes appear in every split and the test set is source-disjoint.

### Stage 2 - Manipulation-type classification

- Add labels for `copy_move`, `splicing`, `removal`, and `morphing` only where the dataset supports them.
- Train a separate classifier for forged images, or use a multi-task head after Stage 1 is stable.
- Report per-class precision, recall, F1, and confusion matrix.
- **Exit criterion:** no unsupported type is presented as a model prediction.

### Stage 3 - Forgery localization

- Train a U-Net or equivalent segmentation model using tampering masks.
- Evaluate IoU, Dice, pixel precision, and pixel recall.
- Compare predicted masks with Grad-CAM, but keep them as separate outputs.
- **Exit criterion:** localization metrics are measured on held-out images with masks.

### Stage 4 - Forensic evidence engine

- Add copy-move feature matching with SIFT or ORB.
- Add region-level noise, edge, texture, and compression comparisons.
- Return evidence as indicators with strength and limitations, not absolute proof.
- **Exit criterion:** each evidence rule has controlled examples and false-positive checks.

### Stage 5 - Human-readable explanation

- Combine classifier output, type prediction, localization, and evidence indicators.
- Generate explanations such as: “Potential copy-move: similar local features were found in two spatially separated regions.”
- Clearly distinguish `model attribution`, `suspected region`, and `supporting forensic evidence`.
- **Exit criterion:** every explanation is traceable to an actual measured output.

### Stage 6 - Application integration

- Extend the image API response with type, mask, evidence, and explanation fields.
- Update the React image page to show original image, predicted mask, Grad-CAM, evidence, and limitations.
- Implement reports only after the response contract is stable.
- Keep video, history, and signature functionality labelled as prototype or future work until implemented and tested.

### Stage 7 - Final validation and presentation

- Run the complete test suite and a real-checkpoint integration suite.
- Record dataset counts, split policy, training configuration, metrics, and known limitations.
- Do not present validation AUC from five samples as final accuracy.

## Execution status

- [x] Existing image training and inference pipeline inspected.
- [x] Existing test suite verified: 31 passed.
- [x] Existing local data counted and checkpoint metadata inspected.
- [x] Generated `datasets/manifests/image_manifest.csv` from the local CASIA subset.
- [ ] Import a larger labelled dataset with masks.
- [ ] Generate the unified manifest.
- [ ] Retrain Stage 1 on source-disjoint splits.
- [ ] Add manipulation-type classification.
- [ ] Add mask-based localization.
- [ ] Add evidence engine and explanation response.
- [ ] Integrate and validate the expanded UI/report.

## Current blocker

The full training stages cannot be executed honestly until a larger dataset with masks and manipulation labels is available. The current local folders contain only a small classification subset and no mask directory.
