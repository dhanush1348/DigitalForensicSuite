"""
Application-wide configuration via environment variables.

Usage in services:
    from app.core.config import settings
    model_path = settings.signature_model_path

Environment variables (create a .env file in the backend/ directory):
    SIGNATURE_MODEL_PATH=../models/signature/best_siamese.pth
    IMAGE_MODEL_PATH=../models/image_forgery/best_efficientnet.pth
    UPLOAD_DIR=../uploads
    MAX_FILE_MB=20
    ALLOWED_IMAGE_EXTS=.jpg,.jpeg,.png,.bmp,.tif,.tiff
    ALLOWED_SIG_EXTS=.jpg,.jpeg,.png,.bmp
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Model checkpoints (relative to project root)
    signature_model_path: str = "../models/signature/best_siamese.pth"
    image_model_path: str = "../models/image_forgery/best_efficientnet_casia_full_gpu.pth"

    # Upload directory
    upload_dir: str = "../uploads"

    # File upload limits
    max_file_mb: int = 20

    # Allowed file extensions
    allowed_image_exts: str = ".jpg,.jpeg,.png,.bmp,.tif,.tiff"
    allowed_sig_exts: str   = ".jpg,.jpeg,.png,.bmp"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_image_ext_list(self) -> list[str]:
        return [e.strip() for e in self.allowed_image_exts.split(",")]

    @property
    def allowed_sig_ext_list(self) -> list[str]:
        return [e.strip() for e in self.allowed_sig_exts.split(",")]

    @property
    def max_file_bytes(self) -> int:
        return self.max_file_mb * 1024 * 1024


settings = Settings()
