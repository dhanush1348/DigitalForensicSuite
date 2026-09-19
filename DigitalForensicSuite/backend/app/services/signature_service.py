"""
Service layer for Signature Verification.

Responsibilities:
  - Save uploaded files to the uploads directory
  - Lazy-load the Siamese ResNet18 model (singleton — loaded once per process)
  - Call the inference module
  - Return a dict matching SignatureResponse schema

The model loading is deferred until the first request so the API server
starts instantly even if the checkpoint file doesn't exist yet.
"""

import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

import sys
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import settings
from inference.predict_signature import load_model as _load_model, predict as _predict


# Module-level model handle (None until first request)
_model   = None
_device  = None


def _get_model():
    global _model, _device
    if _model is None:
        try:
            ckpt = str(ROOT / settings.signature_model_path.lstrip("../"))
            _model, _device = _load_model(ckpt_path=ckpt)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Signature model not available: {exc}",
            )
    return _model, _device


async def _save_upload(upload: UploadFile, suffix: str) -> Path:
    """Save an UploadFile to the uploads directory and return its path."""
    upload_dir = ROOT / settings.upload_dir.lstrip("../")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Validate extension
    ext = Path(upload.filename or "file").suffix.lower()
    if ext not in settings.allowed_sig_ext_list:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{ext}'. Allowed: {settings.allowed_sig_ext_list}",
        )

    dest = upload_dir / f"{uuid.uuid4().hex}_{suffix}{ext}"
    async with aiofiles.open(dest, "wb") as f:
        content = await upload.read()
        if len(content) > settings.max_file_bytes:
            raise HTTPException(status_code=413, detail="File too large.")
        await f.write(content)
    return dest


async def compare(reference: UploadFile, questioned: UploadFile) -> dict:
    """
    Save both uploads, run Siamese inference, and return result dict.

    Args:
        reference:  Known genuine signature upload.
        questioned: Signature to verify.

    Returns:
        Dict matching SignatureResponse schema.
    """
    model, device = _get_model()

    ref_path   = await _save_upload(reference,  "ref")
    query_path = await _save_upload(questioned, "query")

    try:
        result = _predict(
            ref_path=str(ref_path),
            query_path=str(query_path),
            model=model,
            device=device,
        )
    finally:
        # Clean up temp files
        ref_path.unlink(missing_ok=True)
        query_path.unlink(missing_ok=True)

    return result
