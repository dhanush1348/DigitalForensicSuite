"""
Signature inference + Grad-CAM heatmap generation.

Public API:
    model = load_model(ckpt_path)
    result = predict(ref_path, query_path, model)

    result = {
        "verdict":          "GENUINE" | "FORGED",
        "similarity_percent": float (0–100),
        "confidence":        float (0–1),
        "heatmap_b64":       str  (base64-encoded PNG of Grad-CAM on query image),
        "processing_time_ms": float,
    }

CLI:
    python inference/predict_signature.py \\
        --ref    path/to/ref.png \\
        --query  path/to/query.png \\
        [--ckpt  models/signature/best_siamese.pth]
"""

import argparse
import base64
import io
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from preprocessing.signature_preprocessing import preprocess_signature
from models.signature.siamese_resnet import SiameseResNet18

# Decision threshold on cosine similarity (0–1 scale)
SIMILARITY_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

_cached_model: SiameseResNet18 | None = None
_cached_device: torch.device | None   = None


def load_model(
    ckpt_path: str | None = None,
    device: torch.device | None = None,
) -> tuple[SiameseResNet18, torch.device]:
    """
    Load (or return cached) SiameseResNet18.

    Args:
        ckpt_path: Path to .pth checkpoint. If None, loads untrained weights
                   (useful for smoke testing without a trained model).
        device:    Target device. Auto-detected if None.

    Returns:
        (model, device)
    """
    global _cached_model, _cached_device

    if _cached_model is not None:
        return _cached_model, _cached_device

    dev = device or (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))
    model = SiameseResNet18(pretrained=ckpt_path is None)

    if ckpt_path and Path(ckpt_path).exists():
        ckpt = torch.load(ckpt_path, map_location=dev)
        model.load_state_dict(ckpt["state_dict"])
        print(f"[Signature] Loaded checkpoint: {ckpt_path}  (AUC={ckpt.get('auc', '?'):.4f})")
    elif ckpt_path:
        print(f"[Signature] WARNING — checkpoint not found: {ckpt_path}. Using untrained weights.")
    else:
        print("[Signature] No checkpoint specified — using untrained ResNet18 weights.")

    model.to(dev)
    model.eval()

    _cached_model  = model
    _cached_device = dev
    return model, dev


# ---------------------------------------------------------------------------
# Grad-CAM helper
# ---------------------------------------------------------------------------

def _generate_heatmap(
    model: SiameseResNet18,
    query_tensor: torch.Tensor,   # (1, 3, H, W) on CPU
    query_pil: Image.Image,
    device: torch.device,
) -> str:
    """Return base64-encoded PNG of Grad-CAM overlay on the query signature."""

    # Target layer: last conv layer of the shared encoder (layer4)
    target_layer = model.encoder.features[-3]  # ResNet18 layer4

    # GradCAM needs a forward that returns logits. We wrap the encoder output distance.
    class _EmbWrapper(torch.nn.Module):
        def __init__(self, enc):
            super().__init__()
            self.enc = enc

        def forward(self, x):
            feat = self.enc.features(x)          # (1, 512, 1, 1)
            emb  = self.enc.embed(feat)           # (1, 128)
            norm = F.normalize(emb, p=2, dim=1)
            # Return "logits" shape (1, 1) — cam treats this as class 0
            return norm.sum(dim=1, keepdim=True)

    wrapper = _EmbWrapper(model.encoder).to(device)
    wrapper.eval()

    cam = GradCAM(model=wrapper, target_layers=[target_layer])

    input_t = query_tensor.to(device)
    grayscale_cam = cam(input_tensor=input_t)  # (1, H, W) in [0,1]
    grayscale_cam = grayscale_cam[0]

    # Overlay on query image
    query_rgb = np.array(query_pil.resize((256, 256)).convert("RGB"), dtype=np.float32) / 255.0
    overlay   = show_cam_on_image(query_rgb, grayscale_cam, use_rgb=True)

    # Encode to PNG base64
    pil_out = Image.fromarray(overlay)
    buf = io.BytesIO()
    pil_out.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ---------------------------------------------------------------------------
# Public predict function
# ---------------------------------------------------------------------------

def predict(
    ref_path:   str,
    query_path: str,
    model: SiameseResNet18,
    device: torch.device,
) -> dict:
    """
    Run Siamese inference and produce Grad-CAM on the query image.

    Returns dict with verdict, similarity_percent, confidence, heatmap_b64,
    and processing_time_ms.
    """
    t0 = time.perf_counter()

    ref_tensor   = preprocess_signature(ref_path).unsqueeze(0)    # (1, 3, 256, 256)
    query_tensor = preprocess_signature(query_path).unsqueeze(0)
    query_pil    = Image.open(query_path)

    with torch.no_grad():
        sim, _, _ = model(ref_tensor.to(device), query_tensor.to(device))

    sim_val = sim.item()  # cosine similarity ∈ [0, 1]

    verdict    = "GENUINE" if sim_val >= SIMILARITY_THRESHOLD else "FORGED"
    confidence = sim_val if verdict == "GENUINE" else (1.0 - sim_val)

    heatmap_b64 = _generate_heatmap(model, query_tensor, query_pil, device)

    elapsed_ms = (time.perf_counter() - t0) * 1000

    return {
        "verdict":             verdict,
        "similarity_percent":  round(sim_val * 100, 2),
        "confidence":          round(confidence, 4),
        "heatmap_b64":         heatmap_b64,
        "processing_time_ms":  round(elapsed_ms, 1),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Signature verification inference")
    parser.add_argument("--ref",   required=True, help="Reference (genuine) signature image")
    parser.add_argument("--query", required=True, help="Questioned signature image")
    parser.add_argument("--ckpt",  default="models/signature/best_siamese.pth",
                        help="Path to trained checkpoint")
    args = parser.parse_args()

    model, device = load_model(args.ckpt)
    result = predict(args.ref, args.query, model, device)

    print(f"\nVerdict   : {result['verdict']}")
    print(f"Similarity: {result['similarity_percent']:.1f}%")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Time      : {result['processing_time_ms']:.1f} ms")
    print(f"Heatmap   : {result['heatmap_b64'][:40]}...  ({len(result['heatmap_b64'])} chars)")
