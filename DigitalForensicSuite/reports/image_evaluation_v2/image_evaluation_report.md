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
| Accuracy | 1.0000 |
| ROC-AUC | 1.0000 |
| Authentic precision | 1.0000 |
| Authentic recall | 1.0000 |
| Authentic F1 | 1.0000 |
| Forged precision | 1.0000 |
| Forged recall | 1.0000 |
| Forged F1 | 1.0000 |

## Confusion Matrix

Rows are true labels and columns are predicted labels. The order is AUTHENTIC, FORGED.

| | Predicted AUTHENTIC | Predicted FORGED |
|---|---:|---:|
| True AUTHENTIC | 3 | 0 |
| True FORGED | 0 | 2 |

## Detailed Classification Report

```text
              precision    recall  f1-score   support

   AUTHENTIC       1.00      1.00      1.00         3
      FORGED       1.00      1.00      1.00         2

    accuracy                           1.00         5
   macro avg       1.00      1.00      1.00         5
weighted avg       1.00      1.00      1.00         5
```

These metrics describe the labeled evaluation split only. They are not a substitute for a source-disjoint test set or external validation.
