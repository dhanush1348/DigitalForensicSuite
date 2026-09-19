"""
Unit tests for preprocessing modules.

Tests use synthetic (randomly generated) PIL images so no dataset
is required to run them.

Run:
    pytest tests/test_preprocessing.py -v
"""

import io
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_synthetic_image(width=256, height=256, color="white", fmt="PNG") -> str:
    """Create a temporary synthetic image file and return its path."""
    import tempfile, os
    img = Image.new("RGB", (width, height), color=color)
    # Draw some random dark strokes to simulate a signature
    arr = np.array(img)
    arr[50:80, 40:200] = [0, 0, 0]    # horizontal stroke
    arr[40:180, 90:120] = [0, 0, 0]   # vertical stroke
    img = Image.fromarray(arr.astype(np.uint8))

    suffix = ".png" if fmt == "PNG" else ".jpg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    img.save(tmp.name, format=fmt)
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Signature preprocessing tests
# ---------------------------------------------------------------------------

class TestSignaturePreprocessing:
    def test_returns_tensor_with_correct_shape(self):
        """preprocess_signature should return a (3, 256, 256) float tensor."""
        import torch
        from preprocessing.signature_preprocessing import preprocess_signature

        path = _make_synthetic_image()
        tensor = preprocess_signature(path)
        assert tensor.shape == (3, 256, 256), f"Unexpected shape: {tensor.shape}"
        assert tensor.dtype == torch.float32

    def test_file_not_found_raises(self):
        """preprocess_signature should raise FileNotFoundError for missing files."""
        from preprocessing.signature_preprocessing import preprocess_signature
        with pytest.raises(FileNotFoundError):
            preprocess_signature("/nonexistent/path/sig.png")

    def test_normalized_values_in_range(self):
        """Output tensor values should span a reasonable range after ImageNet normalization."""
        from preprocessing.signature_preprocessing import preprocess_signature
        import torch
        path   = _make_synthetic_image()
        tensor = preprocess_signature(path)
        assert tensor.min().item() < 0.0, "Expected negative values after ImageNet normalization"
        assert tensor.max().item() < 10.0, "Unexpectedly large max value"

    def test_build_cedar_pairs_missing_dir(self, tmp_path):
        """build_cedar_pairs should raise FileNotFoundError when dirs are absent."""
        from preprocessing.signature_preprocessing import build_cedar_pairs
        with pytest.raises(FileNotFoundError):
            build_cedar_pairs(str(tmp_path / "nonexistent_cedar"))

    def test_build_cedar_pairs_structure(self, tmp_path):
        """build_cedar_pairs should return (str, str, int) tuples."""
        from preprocessing.signature_preprocessing import build_cedar_pairs

        # Create minimal CEDAR-like structure
        org_dir  = tmp_path / "full_org"
        forg_dir = tmp_path / "full_forg"
        org_dir.mkdir(); forg_dir.mkdir()

        for i in range(1, 4):
            for s in range(1, 5):
                img = Image.new("L", (64, 64), color=200)
                img.save(org_dir  / f"original_{i}_{s}.png")
                img.save(forg_dir / f"forgeries_{i}_{s}.png")

        pairs = build_cedar_pairs(str(tmp_path))
        assert len(pairs) > 0, "Expected at least one pair"
        for path_a, path_b, label in pairs:
            assert isinstance(path_a, str)
            assert isinstance(path_b, str)
            assert label in (0, 1)


# ---------------------------------------------------------------------------
# Image preprocessing tests
# ---------------------------------------------------------------------------

class TestImagePreprocessing:
    def test_generate_ela_returns_pil_image(self):
        """generate_ela_image should return a PIL.Image in RGB mode."""
        from preprocessing.image_preprocessing import generate_ela_image
        path = _make_synthetic_image(fmt="PNG")
        ela  = generate_ela_image(path)
        assert isinstance(ela, Image.Image)
        assert ela.mode == "RGB"

    def test_preprocess_image_tensor_shape(self):
        """preprocess_image should return a (3, 224, 224) float tensor."""
        import torch
        from preprocessing.image_preprocessing import preprocess_image
        path   = _make_synthetic_image(fmt="PNG")
        tensor = preprocess_image(path)
        assert tensor.shape == (3, 224, 224), f"Unexpected shape: {tensor.shape}"
        assert tensor.dtype == torch.float32

    def test_build_casia_missing_dir(self, tmp_path):
        """build_casia_dataset should raise FileNotFoundError for bad root."""
        from preprocessing.image_preprocessing import build_casia_dataset
        with pytest.raises(FileNotFoundError):
            build_casia_dataset(str(tmp_path / "no_such_dir"))

    def test_build_casia_labels(self, tmp_path):
        """build_casia_dataset should return 0 for Au and 1 for Tp."""
        from preprocessing.image_preprocessing import build_casia_dataset

        au_dir = tmp_path / "Au"
        tp_dir = tmp_path / "Tp"
        au_dir.mkdir(); tp_dir.mkdir()

        for i in range(3):
            img = Image.new("RGB", (64, 64), color=(200, 200, 200))
            img.save(au_dir / f"Au_sample_{i}.jpg")
            img.save(tp_dir / f"Tp_sample_{i}.jpg")

        samples = build_casia_dataset(str(tmp_path))
        labels  = [l for _, l in samples]
        assert set(labels) == {0, 1}, "Expected both authentic (0) and tampered (1) labels"
