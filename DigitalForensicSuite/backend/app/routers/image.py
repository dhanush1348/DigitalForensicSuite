from fastapi import APIRouter, UploadFile, File

from app.services import image_service

router = APIRouter()


@router.post("/")
async def analyze_image(file: UploadFile = File(...)):
    """
    Run ELA + CNN forgery detection on an uploaded image.
    Returns: prediction, confidence, forgery_type, heatmap_url
    """
    result = await image_service.predict(file)
    return result
