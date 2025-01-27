from fastapi import FastAPI, File, UploadFile, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import tempfile
from liveness_utils import AWSLivenessDetector
import uuid
import logging
from functools import lru_cache

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(title="DeepGuard 2.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
@lru_cache()
def get_liveness_detector():
    try:
        return AWSLivenessDetector()
    except Exception as e:
        logger.error(f"Failed to initialize AWS Liveness Detector: {str(e)}")
        raise

async def save_upload(file: UploadFile) -> str:
    """Save uploaded file to temporary location"""
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            return tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

def cleanup_files(file_paths: list):
    """Clean up temporary files"""
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")

@app.post("/vkyc")
async def video_kyc(
    video: UploadFile = File(...),
    id_card: UploadFile = File(...)
):
    """Endpoint for video KYC verification"""
    temp_files = []
    try:
        # Get liveness detector instance
        liveness = get_liveness_detector()
        
        # Save uploaded files
        video_path = await save_upload(video)
        id_path = await save_upload(id_card)
        temp_files.extend([video_path, id_path])

        # Create session ID
        session_id = str(uuid.uuid4())

        # Perform VKYC check
        result = liveness.full_vkyc_check(
            session_id=session_id,
            id_card_path=id_path,
            video_path=video_path
        )

        return result

    except Exception as e:
        logger.error(f"VKYC processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Ensure cleanup happens even if processing fails
        cleanup_files(temp_files)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)