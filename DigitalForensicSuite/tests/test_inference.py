"""
Smoke tests for inference modules.

These tests run with untrained model weights (no checkpoint required).
They verify that the model architectures and inference pipelines are
correctly wired end-to-end.

Run:
    pytest tests/test_inference.py -v
"""

import sys
from pathlib import Path
import tempfile

import numpy as np
import pytest
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_temp_image(color=(200, 200, 200), size=(224, 224), fmt="JPEG") -> str:
    img = Image.new("RGB", size, color=color)
    suffix = ".jpg" if fmt == "JPEG" else ".png"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    img.save(tmp.name, format=fmt)
    tmp.close()
    return tmp.name


def _make_temp_sig(size=(256, 256)) -> str:
    arr = np.ones((*size, 3), dtype=np.uint8) * 240
    arr[60:90, 30:200] = 20   # dark stroke
    img = Image.fromarray(arr)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp.name)
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Model definition tests
# ---------------------------------------------------------------------------

class TestSiameseResNet18:
    def test_forward_output_shapes(self):
        """SiameseResNet18 forward should return (sim, emb_a, emb_b) with correct shapes."""
        from models.signature.siamese_resnet import SiameseResNet18
        model = SiameseResNet18(pretrained=False)
        model.eval()

        x = torch.randn(2, 3, 256, 256)
        with torch.no_grad():
            sim, emb_a, emb_b = model(x, x)

        assert sim.shape   == (2,),   f"Expected (2,), got {sim.shape}"
        assert emb_a.shape == (2, 128), f"Expected (2,128), got {emb_a.shape}"
        assert emb_b.shape == (2, 128)

    def test_embeddings_are_l2_normalized(self):
        """Embeddings should be unit-norm (L2 normalized)."""
        from models.signature.siamese_resnet import SiameseResNet18
        model = SiameseResNet18(pretrained=False)
        model.eval()

        x = torch.randn(3, 3, 256, 256)
        with torch.no_grad():
            _, emb_a, _ = model(x, x)

        norms = torch.norm(emb_a, p=2, dim=1)
        assert torch.allclose(norms, torch.ones(3), atol=1e-5), f"Embeddings not unit-norm: {norms}"

    def test_similarity_in_range(self):
        """Similarity output should be in [0, 1]."""
        from models.signature.siamese_resnet import SiameseResNet18
        model = SiameseResNet18(pretrained=False)
        model.eval()

        x = torch.randn(4, 3, 256, 256)
        with torch.no_grad():
            sim, _, _ = model(x, x)

        assert (sim >= 0.0).all() and (sim <= 1.0).all(), f"Similarity out of [0,1]: {sim}"

    def test_contrastive_loss_positive(self):
        """ContrastiveLoss should return a non-negative scalar."""
        from models.signature.siamese_resnet import ContrastiveLoss, SiameseResNet18
        import torch.nn.functional as F

        loss_fn = ContrastiveLoss(margin=1.0)
        emb_a = F.normalize(torch.randn(4, 128), p=2, dim=1)
        emb_b = F.normalize(torch.randn(4, 128), p=2, dim=1)
        labels = torch.tensor([0, 1, 0, 1], dtype=torch.long)

        loss = loss_fn(emb_a, emb_b, labels)
        assert loss.item() >= 0.0, f"Loss should be non-negative, got {loss.item()}"
        assert loss.ndim == 0, "Loss should be a scalar"


class TestEfficientNetForgery:
    def test_forward_output_shape(self):
        """EfficientNetForgery forward should return (B, 2) logits."""
        from models.image_forgery.efficientnet_forgery import EfficientNetForgery
        model = EfficientNetForgery(pretrained=False)
        model.eval()

        x = torch.randn(2, 3, 224, 224)
        with torch.no_grad():
            logits = model(x)

        assert logits.shape == (2, 2), f"Expected (2, 2), got {logits.shape}"

    def test_cam_target_layer_accessible(self):
        """get_cam_target_layer() should return a valid nn.Module."""
        import torch.nn as nn
        from models.image_forgery.efficientnet_forgery import EfficientNetForgery
        model  = EfficientNetForgery(pretrained=False)
        target = model.get_cam_target_layer()
        assert isinstance(target, nn.Module), "Target layer should be an nn.Module"


# ---------------------------------------------------------------------------
# Inference pipeline smoke tests
# ---------------------------------------------------------------------------

class TestSignatureInference:
    def test_predict_returns_expected_keys(self):
        """predict_signature.predict() should return all required keys."""
        from inference.predict_signature import load_model, predict

        model, device = load_model(ckpt_path=None)   # untrained weights
        ref_path   = _make_temp_sig()
        query_path = _make_temp_sig()

        result = predict(ref_path, query_path, model, device)

        required_keys = {"verdict", "similarity_percent", "confidence", "heatmap_b64", "processing_time_ms"}
        assert required_keys.issubset(result.keys()), f"Missing keys: {required_keys - result.keys()}"

    def test_predict_verdict_is_valid(self):
        """Verdict should be GENUINE or FORGED."""
        from inference.predict_signature import load_model, predict
        model, device = load_model(ckpt_path=None)
        result = predict(_make_temp_sig(), _make_temp_sig(), model, device)
        assert result["verdict"] in ("GENUINE", "FORGED")

    def test_predict_similarity_in_range(self):
        """similarity_percent should be between 0 and 100."""
        from inference.predict_signature import load_model, predict
        model, device = load_model(ckpt_path=None)
        result = predict(_make_temp_sig(), _make_temp_sig(), model, device)
        assert 0.0 <= result["similarity_percent"] <= 100.0

    def test_predict_heatmap_is_base64(self):
        """heatmap_b64 should be a non-empty base64 string."""
        import base64
        from inference.predict_signature import load_model, predict
        model, device = load_model(ckpt_path=None)
        result = predict(_make_temp_sig(), _make_temp_sig(), model, device)
        assert len(result["heatmap_b64"]) > 100
        base64.b64decode(result["heatmap_b64"])   # should not raise


class TestImageInference:
    def test_predict_returns_expected_keys(self):
        """predict_image.predict() should return all required keys."""
        from inference.predict_image import load_model, predict
        model, device = load_model(ckpt_path=None)
        result = predict(_make_temp_image(), model, device)

        required_keys = {"verdict", "confidence", "p_authentic", "p_forged", "heatmap_b64", "processing_time_ms"}
        assert required_keys.issubset(result.keys())

    def test_predict_verdict_is_valid(self):
        """Verdict should be AUTHENTIC or FORGED."""
        from inference.predict_image import load_model, predict
        model, device = load_model(ckpt_path=None)
        result = predict(_make_temp_image(), model, device)
        assert result["verdict"] in ("AUTHENTIC", "FORGED")

    def test_predict_probabilities_sum_to_one(self):
        """p_authentic + p_forged should be approximately 1.0 (softmax output)."""
        from inference.predict_image import load_model, predict
        model, device = load_model(ckpt_path=None)
        result = predict(_make_temp_image(), model, device)
        total = result["p_authentic"] + result["p_forged"]
        assert abs(total - 1.0) < 0.01, f"Probabilities don't sum to 1: {total}"
