"""
Service layer for Image Forgery Detection.

Responsibilities:
  - Save the uploaded image to the uploads directory
  - Lazy-load EfficientNet-B0 (singleton)
  - Call the inference module
  - Return a dict matching ImageForensicsResponse schema
"""

import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile

import sys
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import settings
from inference.predict_image import load_model as _load_model, predict as _predict


_model  = None
_device = None


def _get_model():
    global _model, _device
    if _model is None:
        try:
            ckpt = str(ROOT / settings.image_model_path.lstrip("../"))
            _model, _device = _load_model(ckpt_path=ckpt)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Image forgery model not available: {exc}",
            )
    return _model, _device


async def _save_upload(upload: UploadFile) -> Path:
    upload_dir = ROOT / settings.upload_dir.lstrip("../")
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(upload.filename or "file").suffix.lower()
    if ext not in settings.allowed_image_ext_list:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{ext}'. Allowed: {settings.allowed_image_ext_list}",
        )

    dest = upload_dir / f"{uuid.uuid4().hex}_img{ext}"
    async with aiofiles.open(dest, "wb") as f:
        content = await upload.read()
        if len(content) > settings.max_file_bytes:
            raise HTTPException(status_code=413, detail="File too large.")
        await f.write(content)
    return dest


async def predict(file: UploadFile) -> dict:
    """
    Save the upload, run EfficientNet-B0 forgery detection, return result dict.

    Args:
        file: Uploaded image file.

    Returns:
        Dict matching ImageForensicsResponse schema.
    """
    model, device = _get_model()
    image_path    = await _save_upload(file)

    try:
        result = _predict(
            image_path=str(image_path),
            model=model,
            device=device,
        )
    finally:
        image_path.unlink(missing_ok=True)

    return result
