"""
Signature Verification router.

Endpoint:
    POST /signature/
        reference  : UploadFile (known genuine signature)
        questioned : UploadFile (signature to verify)

    Returns SignatureResponse JSON.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.schemas.signature import SignatureResponse
from app.services import signature_service

router = APIRouter()


@router.post(
    "/",
    response_model=SignatureResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify a handwritten signature",
    description=(
        "Upload a **reference** (known genuine) and a **questioned** signature image. "
        "Returns a Genuine/Forged verdict, cosine similarity score, confidence, "
        "and a Grad-CAM heatmap highlighting the most influential pen-stroke regions."
    ),
)
async def verify_signature(
    reference:  UploadFile = File(..., description="Known genuine signature (JPEG/PNG/BMP)"),
    questioned: UploadFile = File(..., description="Signature to verify (JPEG/PNG/BMP)"),
):
    """
    Run Siamese ResNet18 comparison between reference and questioned signatures.

    - **verdict**: GENUINE or FORGED
    - **similarity_percent**: 0–100 cosine similarity
    - **confidence**: model certainty (0–1)
    - **heatmap_b64**: base64 PNG Grad-CAM overlay on the questioned image
    """
    try:
        result = await signature_service.compare(reference, questioned)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {exc}",
        )
    return result
