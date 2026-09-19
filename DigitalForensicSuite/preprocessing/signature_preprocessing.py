"""
Signature preprocessing for the Siamese ResNet18 verification model.

Pipeline:
  RGB load → Grayscale → Otsu threshold → morphological clean
  → resize to target → normalize to ImageNet stats → torch.Tensor

Also provides CEDAR dataset pair builder.

CEDAR directory layout expected:
  cedar_root/
    full_org/          ← genuine signatures
      original_<writer>_<sample>.png
    full_forg/         ← forged signatures
      forgeries_<writer>_<sample>.png

Each writer has 24 genuine and 24 forgeries.
"""

import os
import random
from pathlib import Path
from typing import Tuple, List

import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms


# ---------------------------------------------------------------------------
# Image-level transforms
# ---------------------------------------------------------------------------

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

_sig_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


def preprocess_signature(image_path: str, size: Tuple[int, int] = (256, 256)) -> torch.Tensor:
    """
    Load a signature image and return a normalized RGB tensor of shape (3, H, W).

    Steps:
      1. Load as grayscale via OpenCV
      2. Otsu threshold → binary
      3. Morphological opening (remove noise) + closing (fill gaps)
      4. Convert back to 3-channel PIL image (white background, black strokes)
      5. Resize + normalize to ImageNet stats

    Args:
        image_path: Path to the signature image.
        size: Target (height, width) — must match model input size.

    Returns:
        torch.Tensor of shape (3, H, W), dtype float32.
    """
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    # Otsu binarization
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Morphological cleaning
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN,  kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Invert back: black strokes on white background → RGB
    cleaned_inv = cv2.bitwise_not(cleaned)
    pil_img = Image.fromarray(cleaned_inv).convert("RGB")

    return _sig_transform(pil_img)


# ---------------------------------------------------------------------------
# CEDAR pair builder
# ---------------------------------------------------------------------------

def build_cedar_pairs(
    root_dir: str,
    genuine_ratio: float = 0.5,
    seed: int = 42,
) -> List[Tuple[str, str, int]]:
    """
    Build (img_a, img_b, label) triplets from a CEDAR root directory.

    label = 0 → genuine pair (same writer, both genuine)
    label = 1 → forged pair (genuine + forgery of same writer)

    Args:
        root_dir:       Path to CEDAR root (contains full_org/ and full_forg/).
        genuine_ratio:  Fraction of pairs that are genuine (rest are forged).
        seed:           Random seed for reproducibility.

    Returns:
        List of (path_a, path_b, label) tuples.
    """
    root = Path(root_dir)
    genuine_dir = root / "full_org"
    forgery_dir = root / "full_forg"

    if not genuine_dir.exists() or not forgery_dir.exists():
        raise FileNotFoundError(
            f"CEDAR directories not found at {root}. "
            "Expected: full_org/ and full_forg/"
        )

    # Group files by writer index
    genuine_files: dict[int, List[Path]] = {}
    for f in sorted(genuine_dir.glob("*.png")):
        # filename: original_<writer>_<sample>.png
        try:
            writer_idx = int(f.stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        genuine_files.setdefault(writer_idx, []).append(f)

    forgery_files: dict[int, List[Path]] = {}
    for f in sorted(forgery_dir.glob("*.png")):
        # filename: forgeries_<writer>_<sample>.png
        try:
            writer_idx = int(f.stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        forgery_files.setdefault(writer_idx, []).append(f)

    rng = random.Random(seed)
    pairs: List[Tuple[str, str, int]] = []

    for writer_idx in genuine_files:
        g_list = genuine_files[writer_idx]
        f_list = forgery_files.get(writer_idx, [])

        # Genuine pairs: shuffle and pair consecutive
        shuffled = g_list.copy()
        rng.shuffle(shuffled)
        for i in range(0, len(shuffled) - 1, 2):
            pairs.append((str(shuffled[i]), str(shuffled[i + 1]), 0))

        # Forged pairs: genuine + forgery of same writer
        for g, f in zip(g_list, f_list):
            pairs.append((str(g), str(f), 1))

    rng.shuffle(pairs)
    return pairs
