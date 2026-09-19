"""Pydantic response schema for the Signature Verification endpoint."""

from typing import Literal
from pydantic import BaseModel, Field


class SignatureResponse(BaseModel):
    """Response returned by POST /signature/"""

    verdict: Literal["GENUINE", "FORGED"] = Field(
        description="Whether the questioned signature is genuine or forged."
    )
    similarity_percent: float = Field(
        ge=0.0, le=100.0,
        description="Cosine similarity between reference and questioned embeddings, 0–100.",
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Model certainty: distance from the decision boundary (0–1).",
    )
    heatmap_b64: str = Field(
        description="Base64-encoded PNG of Grad-CAM overlay on the questioned signature."
    )
    processing_time_ms: float = Field(
        description="End-to-end inference latency in milliseconds."
    )

    model_config = {"json_schema_extra": {
        "example": {
            "verdict":             "GENUINE",
            "similarity_percent":  78.4,
            "confidence":          0.784,
            "heatmap_b64":         "iVBORw0KGgo...",
            "processing_time_ms":  312.5,
        }
    }}
