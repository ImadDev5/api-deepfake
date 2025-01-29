from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import tempfile
import torch
from efficientnet_pytorch import EfficientNet
from typing import Optional
from liveness_utils import AWSLivenessDetector
from aws_utils import AWSServices
from transaction_monitor import TransactionMonitor
from config import settings
import logging
import uuid
import cv2
import numpy as np
from models import TransactionData


# Configure logging
logging.basicConfig(level=logging.INFO)
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
liveness_detector = AWSLivenessDetector()
aws_services = AWSServices()
transaction_monitor = TransactionMonitor()

def load_model():
    try:
        # Load the correct EfficientNet architecture
        model = EfficientNet.from_pretrained('efficientnet-b4')
        # Modify the classifier layer
        num_features = model._fc.in_features
        model._fc = torch.nn.Linear(num_features, 1)
        # Load the checkpoint
        checkpoint_path = '/home/vortex/api-deepfake/efficientNetFFPP.pth'
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=True)
        if 'state_dict' in checkpoint:
            model.load_state_dict(checkpoint['state_dict'], strict=False)
        else:
            model.load_state_dict(checkpoint, strict=False)
        # Set the model to evaluation mode and move to the appropriate device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = model.eval().to(device)
        logging.info(f"Model loaded successfully on device: {device}")
        return model
    except FileNotFoundError as e:
        logging.error(f"File error: {str(e)}")
    except KeyError as e:
        logging.error(f"Checkpoint format error: Missing key {str(e)}")
    except RuntimeError as e:
        logging.error(f"Runtime error during model loading: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error during model loading: {str(e)}")
    return None

# Load model at startup
settings.deepfake_model = load_model()

async def save_upload(file: UploadFile) -> str:
    """Save uploaded file to temporary location."""
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
        return tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

def cleanup_files(file_paths: list):
    """Clean up temporary files."""
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")

async def analyze_video(path: str) -> dict:
    """Analyze video for deepfake detection."""
    if not settings.deepfake_model:
        return {'error': 'Model unavailable'}
    device = next(settings.deepfake_model.parameters()).device
    cap = cv2.VideoCapture(path)
    predictions = []
    frame_count = 0
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % int(os.getenv('FRAME_SKIP', 5)) == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (settings.video_size, settings.video_size))
                tensor = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float() / 255.0
                tensor = tensor.to(device)
                with torch.no_grad():
                    pred = torch.sigmoid(settings.deepfake_model(tensor)).item()
                    predictions.append(pred)
            frame_count += 1
        return {
            'risk_score': float(np.mean(predictions)) if predictions else 0.5,
            'frames_analyzed': len(predictions)
        }
    finally:
        cap.release()

@app.post("/detect")
async def detect(video: UploadFile = File(...), audio: Optional[UploadFile] = None):
    """Endpoint for detecting deepfakes and voice fraud."""
    temp_files = []
    try:
        video_path = await save_upload(video)
        audio_path = await save_upload(audio) if audio else None
        temp_files.extend([video_path, audio_path] if audio_path else [video_path])
        deepfake_result = await analyze_video(video_path)
        voice_result = aws_services.detect_voice_fraud(audio_path) if audio else None
        return {
            "deepfake": deepfake_result,
            "voice": voice_result
        }
    except Exception as e:
        logger.error(f"Detection failed: {str(e)}")
        raise HTTPException(500, detail=str(e))
    finally:
        cleanup_files(temp_files)

@app.post("/vkyc")
async def video_kyc(video: UploadFile = File(...), id_card: UploadFile = File(...)):
    """Endpoint for Video KYC verification."""
    temp_files = []
    try:
        video_path = await save_upload(video)
        id_path = await save_upload(id_card)
        temp_files.extend([video_path, id_path])
        deepfake_result = await analyze_video(video_path)
        if deepfake_result['risk_score'] > 0.7:
            return {"error": "Deepfake detected", "result": deepfake_result}
        session_id = str(uuid.uuid4())
        result = liveness_detector.full_vkyc_check(
            session_id=session_id,
            id_card_path=id_path,
            video_path=video_path
        )
        return result
    except Exception as e:
        logger.error(f"VKYC processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_files(temp_files)


@app.post("/api/create-session")
async def create_session():
    """Create a new session for liveness detection."""
    try:
        session_id = str(uuid.uuid4())
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-transaction")
async def analyze_transaction(transaction: TransactionData):
    try:
        metadata = {
            'currency': transaction.currency,
            'device_type': transaction.device_type,
            'location': transaction.location
        }
        result = transaction_monitor.analyze_transaction(
            transaction.user_id, transaction.amount, metadata
        )
        return result
    except Exception as e:
        logger.error(f"Transaction analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-jamtara")
async def detect_jamtara(transactions: list):
    """Endpoint for detecting Jamtara-style scam patterns."""
    try:
        result = transaction_monitor.detect_jamtara_patterns(transactions)
        return result
    except Exception as e:
        logger.error(f"Jamtara detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)