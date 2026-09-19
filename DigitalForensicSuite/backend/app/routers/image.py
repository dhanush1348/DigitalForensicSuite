"""
Image Forgery Detection router.

Endpoint:
    POST /image/
        file : UploadFile (image to analyse)

    Returns ImageForensicsResponse JSON.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.image import ImageForensicsResponse
from app.services import image_service

router = APIRouter()


@router.post(
    "/",
    response_model=ImageForensicsResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect image forgery / manipulation",
    description=(
        "Upload any image (JPEG, PNG, BMP, TIFF). "
        "The ELA pipeline extracts compression inconsistencies, then "
        "EfficientNet-B0 classifies the image as **AUTHENTIC** or **FORGED**. "
        "Grad-CAM highlights the tampered regions in the returned heatmap."
    ),
)
async def analyze_image(
    file: UploadFile = File(..., description="Image to analyse (JPEG/PNG/BMP/TIFF)"),
):
    """
    Run EfficientNet-B0 forgery detection with Grad-CAM explainability.

    - **verdict**: AUTHENTIC or FORGED
    - **confidence**: probability of the predicted class
    - **heatmap_b64**: base64 PNG Grad-CAM overlay on the tampered regions
    """
    try:
        result = await image_service.predict(file)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {exc}",
        )
    return result
