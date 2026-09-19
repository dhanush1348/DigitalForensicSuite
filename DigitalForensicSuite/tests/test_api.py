"""
API integration tests using FastAPI TestClient.

These tests verify the HTTP layer (routing, validation, error codes)
without requiring trained model weights. Models are loaded with
untrained weights for smoke testing.

Run:
    pytest tests/test_api.py -v
"""

import io
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

# ── Pre-patch model loading so no real checkpoints are needed ──

import inference.predict_signature as _sig_infer
import inference.predict_image     as _img_infer

_sig_infer._cached_model  = None
_sig_infer._cached_device = None
_img_infer._cached_model  = None
_img_infer._cached_device = None


def _orig_sig_load(ckpt_path=None, device=None):
    from models.signature.siamese_resnet import SiameseResNet18
    import torch
    m = SiameseResNet18(pretrained=False)
    m.eval()
    return m, torch.device("cpu")


def _orig_img_load(ckpt_path=None, device=None):
    from models.image_forgery.efficientnet_forgery import EfficientNetForgery
    import torch
    m = EfficientNetForgery(pretrained=False)
    m.eval()
    return m, torch.device("cpu")


# Monkeypatch at import time
_sig_infer.load_model = _orig_sig_load
_img_infer.load_model = _orig_img_load

import backend.app.services.signature_service as _sig_svc
import backend.app.services.image_service     as _img_svc

_sig_svc._model = None; _sig_svc._device = None
_img_svc._model = None; _img_svc._device = None


# ── Client ────────────────────────────────────────────────────
sys.path.insert(0, str(ROOT / "backend"))
from app.main import app  # noqa: E402

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_png_bytes(size=(128, 128), color=(200, 200, 200)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_jpg_bytes(size=(128, 128)) -> bytes:
    img = Image.new("RGB", size, color=(180, 180, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Image Forgery endpoint
# ---------------------------------------------------------------------------

class TestImageEndpoint:
    def test_missing_file_returns_422(self):
        """POST /image/ with no file should return 422 Unprocessable Entity."""
        resp = client.post("/image/")
        assert resp.status_code == 422

    def test_valid_image_returns_200(self):
        """POST /image/ with a valid PNG should return 200 with expected fields."""
        png_bytes = _make_png_bytes()
        resp = client.post(
            "/image/",
            files={"file": ("test.png", png_bytes, "image/png")},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "verdict"            in data
        assert "confidence"         in data
        assert "heatmap_b64"        in data
        assert "processing_time_ms" in data
        assert data["verdict"] in ("AUTHENTIC", "FORGED")

    def test_verdict_field_type(self):
        """verdict field should be a string literal."""
        png_bytes = _make_png_bytes()
        resp = client.post("/image/", files={"file": ("x.png", png_bytes, "image/png")})
        assert resp.status_code == 200
        assert isinstance(resp.json()["verdict"], str)

    def test_probabilities_sum_to_one(self):
        """p_authentic + p_forged should ≈ 1.0."""
        png_bytes = _make_png_bytes()
        resp = client.post("/image/", files={"file": ("x.png", png_bytes, "image/png")})
        data = resp.json()
        total = data.get("p_authentic", 0) + data.get("p_forged", 0)
        assert abs(total - 1.0) < 0.02


# ---------------------------------------------------------------------------
# Signature Verification endpoint
# ---------------------------------------------------------------------------

class TestSignatureEndpoint:
    def test_missing_files_returns_422(self):
        """POST /signature/ with no files should return 422."""
        resp = client.post("/signature/")
        assert resp.status_code == 422

    def test_missing_one_file_returns_422(self):
        """POST /signature/ with only one file should return 422."""
        png_bytes = _make_png_bytes()
        resp = client.post(
            "/signature/",
            files={"reference": ("ref.png", png_bytes, "image/png")},
        )
        assert resp.status_code == 422

    def test_valid_pair_returns_200(self):
        """POST /signature/ with two valid PNGs should return 200."""
        png_a = _make_png_bytes(color=(220, 220, 220))
        png_b = _make_png_bytes(color=(210, 210, 210))
        resp  = client.post(
            "/signature/",
            files={
                "reference":  ("ref.png",   png_a, "image/png"),
                "questioned": ("query.png", png_b, "image/png"),
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "verdict"             in data
        assert "similarity_percent"  in data
        assert "confidence"          in data
        assert "heatmap_b64"         in data
        assert "processing_time_ms"  in data
        assert data["verdict"] in ("GENUINE", "FORGED")

    def test_similarity_in_valid_range(self):
        """similarity_percent should be between 0 and 100."""
        png = _make_png_bytes()
        resp = client.post(
            "/signature/",
            files={
                "reference":  ("a.png", png, "image/png"),
                "questioned": ("b.png", png, "image/png"),
            },
        )
        data = resp.json()
        assert 0.0 <= data["similarity_percent"] <= 100.0
