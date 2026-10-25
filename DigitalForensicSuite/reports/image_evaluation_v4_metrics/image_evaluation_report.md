# Image Forgery Evaluation Report

## Model

- Backbone: EfficientNet-B0
- Input: Error Level Analysis (ELA), resized to 224x224
- Classes: AUTHENTIC (0), FORGED (1)
- Decision threshold: 0.50
- Samples evaluated: 2523

## Metrics

| Metric | Value |
|---|---:|
| Accuracy | 0.9564 |
| Balanced accuracy | 0.9565 |
| ROC-AUC | 0.9924 |
| PR-AUC | 0.9884 |
| Specificity | 0.9559 |
| False-positive rate | 0.0441 |
| Matthews correlation coefficient | 0.9101 |
| Authentic precision | 0.9702 |
| Authentic recall | 0.9559 |
| Authentic F1 | 0.9630 |
| Forged precision | 0.9370 |
| Forged recall | 0.9571 |
| Forged F1 | 0.9469 |

Diagnostic threshold sweep: forged F1 is highest at approximately `0.50` with F1 `0.9469`. This is not a deployment threshold.

## Confusion Matrix

Rows are true labels and columns are predicted labels. The order is AUTHENTIC, FORGED.

| | Predicted AUTHENTIC | Predicted FORGED |
|---|---:|---:|
| True AUTHENTIC | 1432 | 66 |
| True FORGED | 44 | 981 |

## Detailed Classification Report

```text
              precision    recall  f1-score   support

   AUTHENTIC       0.97      0.96      0.96      1498
      FORGED       0.94      0.96      0.95      1025

    accuracy                           0.96      2523
   macro avg       0.95      0.96      0.95      2523
weighted avg       0.96      0.96      0.96      2523
```

These metrics describe the labeled evaluation split only. They are not a substitute for a source-disjoint test set or external validation.
