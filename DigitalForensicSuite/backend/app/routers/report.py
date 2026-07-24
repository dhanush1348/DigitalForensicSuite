from fastapi import APIRouter

router = APIRouter()


@router.get("/report/{case_id}")
async def get_report(case_id: str):
    """Return the generated PDF forensic report for a given case."""
    raise NotImplementedError


@router.get("/history")
async def get_history():
    """Return past case predictions for the current user/session."""
    raise NotImplementedError
