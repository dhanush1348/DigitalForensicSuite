"""Evaluation and report generation for the image forgery classifier."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    average_precision_score,
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    matthews_corrcoef,
    precision_recall_fscore_support,
    roc_auc_score,
)


CLASS_NAMES = ("AUTHENTIC", "FORGED")


def calculate_metrics(
    labels: Sequence[int],
    forged_probabilities: Sequence[float],
    threshold: float = 0.5,
) -> dict:
    """Calculate thresholded and ranking metrics from labeled predictions."""
    labels_array = np.asarray(labels, dtype=int)
    probabilities = np.asarray(forged_probabilities, dtype=float)
    if labels_array.size == 0 or labels_array.size != probabilities.size:
        raise ValueError("labels and forged_probabilities must be non-empty and equal length")

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")

    predictions = (probabilities >= threshold).astype(int)
    matrix = confusion_matrix(labels_array, predictions, labels=[0, 1])
    true_negative, false_positive, false_negative, true_positive = matrix.ravel()
    precision, recall, f1, support = precision_recall_fscore_support(
        labels_array,
        predictions,
        labels=[0, 1],
        zero_division=0,
    )
    try:
        auc = float(roc_auc_score(labels_array, probabilities))
        pr_auc = float(average_precision_score(labels_array, probabilities))
    except ValueError:
        auc = None
        pr_auc = None

    specificity = true_negative / max(true_negative + false_positive, 1)
    best_threshold = _best_f1_threshold(labels_array, probabilities)
    best_f1 = calculate_metrics(labels_array, probabilities, best_threshold)["per_class"]["FORGED"]["f1"] if best_threshold != threshold else float(f1[1])

    return {
        "class_names": list(CLASS_NAMES),
        "sample_count": int(labels_array.size),
        "threshold": round(float(threshold), 4),
        "confusion_matrix": matrix.tolist(),
        "accuracy": round(float(accuracy_score(labels_array, predictions)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(labels_array, predictions)), 4),
        "roc_auc": round(auc, 4) if auc is not None else None,
        "pr_auc": round(pr_auc, 4) if pr_auc is not None else None,
        "specificity": round(float(specificity), 4),
        "false_positive_rate": round(float(1.0 - specificity), 4),
        "mcc": round(float(matthews_corrcoef(labels_array, predictions)), 4),
        "threshold_diagnostic": {
            "best_forged_f1_threshold": round(float(best_threshold), 4),
            "best_forged_f1": round(float(best_f1), 4),
            "note": "Diagnostic only; select thresholds on a calibration split, not the final test set.",
        },
        "per_class": {
            class_name: {
                "precision": round(float(precision[index]), 4),
                "recall": round(float(recall[index]), 4),
                "f1": round(float(f1[index]), 4),
                "support": int(support[index]),
            }
            for index, class_name in enumerate(CLASS_NAMES)
        },
        "classification_report": classification_report(
            labels_array,
            predictions,
            labels=[0, 1],
            target_names=list(CLASS_NAMES),
            zero_division=0,
        ),
    }


def _best_f1_threshold(labels: np.ndarray, probabilities: np.ndarray) -> float:
    """Find the forged-class F1 threshold for diagnostics, not deployment tuning."""
    thresholds = np.linspace(0.05, 0.95, 19)
    scores = []
    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)
        _, _, f1, _ = precision_recall_fscore_support(
            labels, predictions, labels=[0, 1], zero_division=0
        )
        scores.append(float(f1[1]))
    return float(thresholds[int(np.argmax(scores))])


def write_evaluation_report(metrics: dict, output_dir: str | Path) -> dict[str, str]:
    """Write JSON, Markdown, and confusion-matrix PNG report artifacts."""
    report_dir = Path(output_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = report_dir / "image_evaluation_report.json"
    markdown_path = report_dir / "image_evaluation_report.md"
    matrix_path = report_dir / "confusion_matrix.png"

    json_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    markdown_path.write_text(_markdown_report(metrics), encoding="utf-8")
    _plot_confusion_matrix(metrics["confusion_matrix"], matrix_path)

    return {
        "json": str(json_path),
        "markdown": str(markdown_path),
        "confusion_matrix": str(matrix_path),
    }


def _markdown_report(metrics: dict) -> str:
    matrix = metrics["confusion_matrix"]
    forged = metrics["per_class"]["FORGED"]
    authentic = metrics["per_class"]["AUTHENTIC"]
    auc = "N/A" if metrics["roc_auc"] is None else f"{metrics['roc_auc']:.4f}"
    return f"""# Image Forgery Evaluation Report

## Model

- Backbone: EfficientNet-B0
- Input: Error Level Analysis (ELA), resized to 224x224
- Classes: AUTHENTIC (0), FORGED (1)
- Decision threshold: {metrics['threshold']:.2f}
- Samples evaluated: {metrics['sample_count']}

## Metrics

| Metric | Value |
|---|---:|
| Accuracy | {metrics['accuracy']:.4f} |
| Balanced accuracy | {metrics['balanced_accuracy']:.4f} |
| ROC-AUC | {auc} |
| PR-AUC | {metrics['pr_auc'] if metrics['pr_auc'] is not None else 'N/A'} |
| Specificity | {metrics['specificity']:.4f} |
| False-positive rate | {metrics['false_positive_rate']:.4f} |
| Matthews correlation coefficient | {metrics['mcc']:.4f} |
| Authentic precision | {authentic['precision']:.4f} |
| Authentic recall | {authentic['recall']:.4f} |
| Authentic F1 | {authentic['f1']:.4f} |
| Forged precision | {forged['precision']:.4f} |
| Forged recall | {forged['recall']:.4f} |
| Forged F1 | {forged['f1']:.4f} |

Diagnostic threshold sweep: forged F1 is highest at approximately `{metrics['threshold_diagnostic']['best_forged_f1_threshold']:.2f}` with F1 `{metrics['threshold_diagnostic']['best_forged_f1']:.4f}`. This is not a deployment threshold.

## Confusion Matrix

Rows are true labels and columns are predicted labels. The order is AUTHENTIC, FORGED.

| | Predicted AUTHENTIC | Predicted FORGED |
|---|---:|---:|
| True AUTHENTIC | {matrix[0][0]} | {matrix[0][1]} |
| True FORGED | {matrix[1][0]} | {matrix[1][1]} |

## Detailed Classification Report

```text
{metrics['classification_report']}```

These metrics describe the labeled evaluation split only. They are not a substitute for a source-disjoint test set or external validation.
"""


def _plot_confusion_matrix(matrix: list[list[int]], output_path: Path) -> None:
    figure, axis = plt.subplots(figsize=(5, 4))
    axis.imshow(matrix, cmap="Blues")
    axis.set_title("Image Forgery Confusion Matrix")
    axis.set_xlabel("Predicted label")
    axis.set_ylabel("True label")
    axis.set_xticks([0, 1], CLASS_NAMES)
    axis.set_yticks([0, 1], CLASS_NAMES)
    max_value = max(max(row) for row in matrix) or 1
    for row_index in range(2):
        for column_index in range(2):
            color = "white" if matrix[row_index][column_index] > max_value / 2 else "black"
            axis.text(column_index, row_index, matrix[row_index][column_index], ha="center", va="center", color=color)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
