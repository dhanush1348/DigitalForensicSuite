# Image Forgery Evaluation Report

## Model

- Backbone: EfficientNet-B0
- Input: Error Level Analysis (ELA), resized to 224x224
- Classes: AUTHENTIC (0), FORGED (1)
- Decision threshold: 0.50
- Samples evaluated: 5

## Metrics

| Metric | Value |
|---|---:|
| Accuracy | 0.6000 |
| ROC-AUC | 1.0000 |
| Authentic precision | 0.6000 |
| Authentic recall | 1.0000 |
| Authentic F1 | 0.7500 |
| Forged precision | 0.0000 |
| Forged recall | 0.0000 |
| Forged F1 | 0.0000 |

## Confusion Matrix

Rows are true labels and columns are predicted labels. The order is AUTHENTIC, FORGED.

| | Predicted AUTHENTIC | Predicted FORGED |
|---|---:|---:|
| True AUTHENTIC | 3 | 0 |
| True FORGED | 2 | 0 |

## Detailed Classification Report

```text
              precision    recall  f1-score   support

   AUTHENTIC       0.60      1.00      0.75         3
      FORGED       0.00      0.00      0.00         2

    accuracy                           0.60         5
   macro avg       0.30      0.50      0.38         5
weighted avg       0.36      0.60      0.45         5
```

These metrics describe the labeled evaluation split only. They are not a substitute for a source-disjoint test set or external validation.
