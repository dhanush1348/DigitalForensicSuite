from pathlib import Path

from evaluation.image_evaluation import calculate_metrics, write_evaluation_report


def test_calculate_metrics_returns_confusion_matrix_and_metrics():
    metrics = calculate_metrics(
        labels=[0, 0, 1, 1],
        forged_probabilities=[0.1, 0.8, 0.2, 0.9],
    )

    assert metrics["confusion_matrix"] == [[1, 1], [1, 1]]
    assert metrics["accuracy"] == 0.5
    assert metrics["roc_auc"] == 0.75
    assert "balanced_accuracy" in metrics
    assert "pr_auc" in metrics
    assert "specificity" in metrics
    assert "false_positive_rate" in metrics
    assert "mcc" in metrics
    assert 0.0 <= metrics["threshold_diagnostic"]["best_forged_f1_threshold"] <= 1.0
    assert set(metrics["per_class"]) == {"AUTHENTIC", "FORGED"}
    assert "precision" in metrics["per_class"]["FORGED"]
    assert "recall" in metrics["per_class"]["FORGED"]
    assert "f1" in metrics["per_class"]["FORGED"]


def test_write_evaluation_report_creates_all_artifacts(tmp_path: Path):
    metrics = calculate_metrics([0, 1], [0.1, 0.9])
    paths = write_evaluation_report(metrics, tmp_path)

    for path in paths.values():
        assert Path(path).exists()
        assert Path(path).stat().st_size > 0

    assert "True AUTHENTIC" in Path(paths["markdown"]).read_text(encoding="utf-8")
