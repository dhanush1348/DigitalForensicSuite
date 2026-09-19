"""
Image preprocessing for the EfficientNet-B0 forgery detection model.

Pipelines:
  1. ELA (Error Level Analysis): resave image at low quality, compute amplified
     pixel difference to highlight compression inconsistencies.
  2. Standard preprocessing: resize → normalize → torch.Tensor.

Also provides CASIA v2.0 dataset builder.

CASIA v2.0 Corrected Groundtruth directory layout expected:
  casia_root/
    CASIA2/
      Au/        ← authentic images  (Au_*.jpg / .bmp / .png)
      Tp/        ← tampered images   (Tp_*.jpg / .bmp / .tif)
    masks/       ← binary mask per tampered image (same stem, .png)
                  (from SunnyHaze/CASIA2.0-Corrected-Groundtruth)
"""

import io
import os
import tempfile
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import torch
from torchvision import transforms


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

ELA_QUALITY    = 95   # JPEG re-save quality
ELA_SCALE      = 10   # amplification factor for difference image

_img_transform = transforms.Compose([
    transforms.Resize((224, 224)),   # EfficientNet-B0 default
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


# ---------------------------------------------------------------------------
# ELA
# ---------------------------------------------------------------------------

def generate_ela_image(image_path: str, quality: int = ELA_QUALITY) -> Image.Image:
    """
    Generate an Error Level Analysis (ELA) image.

    Steps:
      1. Open image and re-save as JPEG at `quality`.
      2. Compute pixel-wise absolute difference between original and resaved.
      3. Scale difference by ELA_SCALE to amplify subtle artifacts.

    Args:
        image_path: Path to the input image (any format PIL can read).
        quality:    JPEG re-save quality (default 95).

    Returns:
        PIL.Image in RGB mode — the amplified difference image.
    """
    original = Image.open(image_path).convert("RGB")

    # Re-save to in-memory buffer at reduced quality
    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    recompressed = Image.open(buffer).convert("RGB")

    # Pixel-wise difference
    orig_arr = np.array(original, dtype=np.float32)
    comp_arr = np.array(recompressed, dtype=np.float32)
    diff = np.abs(orig_arr - comp_arr) * ELA_SCALE
    diff = np.clip(diff, 0, 255).astype(np.uint8)

    return Image.fromarray(diff)


def preprocess_image(image_path: str, size: Tuple[int, int] = (224, 224)) -> torch.Tensor:
    """
    Load an image and return a normalized tensor suitable for EfficientNet-B0.

    Uses the ELA image as input (highlights forgery artifacts better than raw RGB).

    Args:
        image_path: Path to source image.
        size:       Target (height, width).

    Returns:
        torch.Tensor of shape (3, H, W), dtype float32.
    """
    ela_img = generate_ela_image(image_path)
    return _img_transform(ela_img)


# ---------------------------------------------------------------------------
# CASIA v2.0 dataset builder
# ---------------------------------------------------------------------------

_IMAGE_EXTS = {".jpg", ".jpeg", ".bmp", ".png", ".tif", ".tiff"}


def build_casia_dataset(
    casia_root: str,
    masks_dir: str | None = None,
) -> List[Tuple[str, int]]:
    """
    Build a flat list of (image_path, label) from a CASIA v2.0 root.

    label = 0 → authentic (Au/)
    label = 1 → tampered  (Tp/)

    Args:
        casia_root: Path to CASIA2/ directory (containing Au/ and Tp/).
        masks_dir:  Optional path to corrected mask directory for reference.
                    Not used for classification labels but logged for debugging.

    Returns:
        List of (absolute_image_path, label) tuples, shuffled.
    """
    root = Path(casia_root)
    au_dir = root / "Au"
    tp_dir = root / "Tp"

    if not au_dir.exists():
        raise FileNotFoundError(f"Authentic dir not found: {au_dir}")
    if not tp_dir.exists():
        raise FileNotFoundError(f"Tampered dir not found: {tp_dir}")

    samples: List[Tuple[str, int]] = []

    for f in au_dir.iterdir():
        if f.suffix.lower() in _IMAGE_EXTS:
            samples.append((str(f.resolve()), 0))

    for f in tp_dir.iterdir():
        if f.suffix.lower() in _IMAGE_EXTS:
            samples.append((str(f.resolve()), 1))

    import random
    random.seed(42)
    random.shuffle(samples)

    print(
        f"[CASIA] Loaded {sum(1 for _, l in samples if l == 0)} authentic "
        f"and {sum(1 for _, l in samples if l == 1)} tampered images."
    )
    return samples
