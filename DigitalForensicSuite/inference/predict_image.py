"""
Image forgery inference + Grad-CAM heatmap generation.

Public API:
    model = load_model(ckpt_path)
    result = predict(image_path, model, device)

    result = {
        "verdict":            "AUTHENTIC" | "FORGED",
        "confidence":          float (0–1),
        "heatmap_b64":         str  (base64-encoded PNG of Grad-CAM overlay),
        "processing_time_ms":  float,
    }

CLI:
    python inference/predict_image.py \\
        --image  path/to/image.jpg \\
        [--ckpt  models/image_forgery/best_efficientnet.pth]
"""

import argparse
import base64
import io
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from preprocessing.image_preprocessing import preprocess_image, generate_ela_image
from models.image_forgery.efficientnet_forgery import EfficientNetForgery

FORGED_CLASS_IDX = 1   # index of the "FORGED" class in the logits


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

_cached_model: EfficientNetForgery | None = None
_cached_device: torch.device | None       = None


def load_model(
    ckpt_path: str | None = None,
    device: torch.device | None = None,
) -> tuple[EfficientNetForgery, torch.device]:
    """
    Load (or return cached) EfficientNetForgery.

    Args:
        ckpt_path: Path to .pth checkpoint. None → untrained weights (smoke test).
        device:    Target device. Auto-detected if None.

    Returns:
        (model, device)
    """
    global _cached_model, _cached_device

    if _cached_model is not None:
        return _cached_model, _cached_device

    dev = device or (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))
    model = EfficientNetForgery(pretrained=ckpt_path is None)

    if ckpt_path and Path(ckpt_path).exists():
        ckpt = torch.load(ckpt_path, map_location=dev)
        model.load_state_dict(ckpt["state_dict"])
        print(f"[Image] Loaded checkpoint: {ckpt_path}  (AUC={ckpt.get('auc', '?'):.4f})")
    elif ckpt_path:
        print(f"[Image] WARNING — checkpoint not found: {ckpt_path}. Using untrained weights.")
    else:
        print("[Image] No checkpoint specified — using untrained EfficientNet-B0 weights.")

    model.to(dev)
    model.eval()

    _cached_model  = model
    _cached_device = dev
    return model, dev


# ---------------------------------------------------------------------------
# Grad-CAM helper
# ---------------------------------------------------------------------------

def _generate_heatmap(
    model: EfficientNetForgery,
    input_tensor: torch.Tensor,   # (1, 3, 224, 224) on CPU
    original_pil: Image.Image,
    device: torch.device,
    target_class: int = FORGED_CLASS_IDX,
) -> str:
    """Return base64-encoded PNG Grad-CAM overlay on the original image."""

    target_layer = model.get_cam_target_layer()

    cam = GradCAM(
        model=model,
        target_layers=[target_layer],
    )

    targets     = [ClassifierOutputTarget(target_class)]
    input_on_dev = input_tensor.to(device)

    grayscale_cam = cam(input_tensor=input_on_dev, targets=targets)  # (1, H, W)
    grayscale_cam = grayscale_cam[0]  # (H, W)

    # Resize original to 224×224 for overlay
    orig_resized = original_pil.resize((224, 224)).convert("RGB")
    orig_rgb     = np.array(orig_resized, dtype=np.float32) / 255.0

    overlay = show_cam_on_image(orig_rgb, grayscale_cam, use_rgb=True)

    pil_out = Image.fromarray(overlay)
    buf     = io.BytesIO()
    pil_out.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _encode_image(image: Image.Image) -> str:
    """Encode a PIL image as a base64 PNG for the explainability response."""
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ---------------------------------------------------------------------------
# Public predict function
# ---------------------------------------------------------------------------

def predict(
    image_path: str,
    model: EfficientNetForgery,
    device: torch.device,
) -> dict:
    """
    Run EfficientNet-B0 forgery detection + Grad-CAM.

    Returns dict with verdict, confidence, heatmap_b64, processing_time_ms.
    """
    t0 = time.perf_counter()

    input_tensor = preprocess_image(image_path).unsqueeze(0)  # (1, 3, 224, 224)
    original_pil = Image.open(image_path)

    with torch.no_grad():
        logits = model(input_tensor.to(device))               # (1, 2)
        probs  = F.softmax(logits, dim=1)                     # (1, 2)

    p_authentic = probs[0, 0].item()
    p_forged    = probs[0, 1].item()

    verdict    = "FORGED"    if p_forged >= 0.5 else "AUTHENTIC"
    confidence = p_forged    if verdict == "FORGED" else p_authentic

    heatmap_b64 = _generate_heatmap(model, input_tensor, original_pil, device)
    ela_b64 = _encode_image(generate_ela_image(image_path).resize((224, 224)))

    if verdict == "FORGED":
        explanation = (
            "The classifier found compression and texture inconsistencies in the ELA view. "
            "Grad-CAM shows the image regions that contributed most to the forged prediction."
        )
        explanation_basis = [
            "ELA compression inconsistency",
            "Grad-CAM high-attribution regions",
            f"Forged probability: {p_forged:.1%}",
        ]
    else:
        explanation = (
            "The classifier did not find enough learned manipulation evidence to label this image forged. "
            "The ELA and Grad-CAM views are supporting evidence, not proof of authenticity."
        )
        explanation_basis = [
            "No strong learned forgery signal",
            "ELA compression evidence",
            f"Authentic probability: {p_authentic:.1%}",
        ]

    elapsed_ms = (time.perf_counter() - t0) * 1000

    return {
        "verdict":            verdict,
        "confidence":         round(confidence, 4),
        "p_authentic":        round(p_authentic, 4),
        "p_forged":           round(p_forged, 4),
        "heatmap_b64":        heatmap_b64,
        "ela_b64":             ela_b64,
        "explanation":        explanation,
        "explanation_basis":  explanation_basis,
        "processing_time_ms": round(elapsed_ms, 1),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image forgery detection inference")
    parser.add_argument("--image", required=True, help="Path to image to analyse")
    parser.add_argument("--ckpt", default="models/image_forgery/best_efficientnet.pth",
                        help="Path to trained checkpoint")
    args = parser.parse_args()

    model, device = load_model(args.ckpt)
    result = predict(args.image, model, device)

    print(f"\nVerdict   : {result['verdict']}")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"P(auth)   : {result['p_authentic']:.4f}  |  P(forged): {result['p_forged']:.4f}")
    print(f"Time      : {result['processing_time_ms']:.1f} ms")
    print(f"Heatmap   : {result['heatmap_b64'][:40]}...  ({len(result['heatmap_b64'])} chars)")
