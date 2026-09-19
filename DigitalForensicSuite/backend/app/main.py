from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import image, video, signature, report

app = FastAPI(
    title="SecureVision-XAI API",
    description="Image, video, and signature forgery detection engine.",
    version="0.1.0",
)

# TODO: restrict origins before production deploy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image.router, prefix="/image", tags=["Image Forensics"])
app.include_router(video.router, prefix="/video", tags=["Video Forensics"])
app.include_router(signature.router, prefix="/signature", tags=["Signature Verification"])
app.include_router(report.router, tags=["Reports & History"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
