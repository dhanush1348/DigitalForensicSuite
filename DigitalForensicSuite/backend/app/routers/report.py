from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parents[3]
IMAGE_REPORT_DIR = ROOT / "reports" / "image_evaluation_v4_metrics"

router = APIRouter()


@router.get("/report/image/evaluation")
async def get_image_evaluation_report():
    """Return the latest image evaluation report as Markdown."""
    report_path = IMAGE_REPORT_DIR / "image_evaluation_report.md"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Image evaluation report has not been generated yet.")
    return FileResponse(report_path, media_type="text/markdown", filename=report_path.name)


@router.get("/report/image/evaluation/{artifact}")
async def get_image_evaluation_artifact(artifact: str):
    """Download the image metrics JSON or confusion-matrix PNG artifact."""
    allowed_artifacts = {
        "metrics": ("image_evaluation_report.json", "application/json"),
        "confusion-matrix": ("confusion_matrix.png", "image/png"),
        "markdown": ("image_evaluation_report.md", "text/markdown"),
    }
    if artifact not in allowed_artifacts:
        raise HTTPException(status_code=404, detail="Unknown image evaluation artifact.")

    filename, media_type = allowed_artifacts[artifact]
    report_path = IMAGE_REPORT_DIR / filename
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Image evaluation report has not been generated yet.")
    return FileResponse(report_path, media_type=media_type, filename=filename)


@router.get("/history")
async def get_history():
    """Return past case predictions for the current user/session."""
    raise NotImplementedError
