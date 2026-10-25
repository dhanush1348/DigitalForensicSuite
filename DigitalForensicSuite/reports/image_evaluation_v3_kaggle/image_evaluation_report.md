# Image Forgery Evaluation Report

## Model

- Backbone: EfficientNet-B0
- Input: Error Level Analysis (ELA), resized to 224x224
- Classes: AUTHENTIC (0), FORGED (1)
- Decision threshold: 0.50
- Samples evaluated: 2522

## Metrics

| Metric | Value |
|---|---:|
| Accuracy | 0.9389 |
| ROC-AUC | 0.9901 |
| Authentic precision | 0.9896 |
| Authentic recall | 0.9051 |
| Authentic F1 | 0.9455 |
| Forged precision | 0.8805 |
| Forged recall | 0.9866 |
| Forged F1 | 0.9306 |

## Confusion Matrix

Rows are true labels and columns are predicted labels. The order is AUTHENTIC, FORGED.

| | Predicted AUTHENTIC | Predicted FORGED |
|---|---:|---:|
| True AUTHENTIC | 1336 | 140 |
| True FORGED | 14 | 1032 |

## Detailed Classification Report

```text
              precision    recall  f1-score   support

   AUTHENTIC       0.99      0.91      0.95      1476
      FORGED       0.88      0.99      0.93      1046

    accuracy                           0.94      2522
   macro avg       0.94      0.95      0.94      2522
weighted avg       0.94      0.94      0.94      2522
```

These metrics describe the labeled evaluation split only. They are not a substitute for a source-disjoint test set or external validation.
