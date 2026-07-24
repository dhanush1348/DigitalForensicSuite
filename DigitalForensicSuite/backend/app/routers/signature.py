from fastapi import APIRouter, UploadFile, File

from app.services import signature_service

router = APIRouter()


@router.post("/")
async def verify_signature(
    reference: UploadFile = File(...),
    questioned: UploadFile = File(...),
):
    """
    Run Siamese network similarity comparison between reference and questioned signatures.
    Returns: similarity_percent, confidence, decision
    """
    result = await signature_service.compare(reference, questioned)
    return result
