from fastapi import APIRouter, UploadFile, File

from app.services import video_service

router = APIRouter()


@router.post("/")
async def analyze_video(file: UploadFile = File(...)):
    """
    Run frame extraction + CNN/Bi-LSTM deepfake detection on an uploaded video.
    Returns: prediction, confidence, manipulated_frames, timeline
    """
    result = await video_service.predict(file)
    return result
