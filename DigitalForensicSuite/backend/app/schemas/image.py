"""Pydantic response schema for the Image Forgery Detection endpoint."""

from typing import Literal
from pydantic import BaseModel, Field


class ImageForensicsResponse(BaseModel):
    """Response returned by POST /image/"""

    verdict: Literal["AUTHENTIC", "FORGED"] = Field(
        description="Whether the image is authentic or has been tampered with."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Probability of the predicted class (0–1).",
    )
    p_authentic: float = Field(
        ge=0.0, le=1.0,
        description="Softmax probability of AUTHENTIC class.",
    )
    p_forged: float = Field(
        ge=0.0, le=1.0,
        description="Softmax probability of FORGED class.",
    )
    heatmap_b64: str = Field(
        description="Base64-encoded PNG of Grad-CAM overlay highlighting tampered regions."
    )
    ela_b64: str = Field(
        default="",
        description="Base64-encoded ELA evidence image used by the classifier."
    )
    explanation: str = Field(
        default="",
        description="Human-readable explanation of the model evidence."
    )
    explanation_basis: list[str] = Field(
        default_factory=list,
        description="Evidence signals shown in the explanation panel."
    )
    processing_time_ms: float = Field(
        description="End-to-end inference latency in milliseconds."
    )

    model_config = {"json_schema_extra": {
        "example": {
            "verdict":            "FORGED",
            "confidence":          0.932,
            "p_authentic":         0.068,
            "p_forged":            0.932,
            "heatmap_b64":         "iVBORw0KGgo...",
            "processing_time_ms":  428.1,
        }
    }}
