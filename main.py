from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import cv2
import numpy as np
import logging
import os
import tempfile
from efficientnet_pytorch import EfficientNet
from dotenv import load_dotenv
from aws_utils import AWSServices
from liveness_utils import AWSLivenessDetector

load_dotenv()
app = FastAPI(title="DeepGuard", version="4.0")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
aws = AWSServices()
liveness_detector = AWSLivenessDetector()

# Model Loading
def load_model():
    try:
        model = EfficientNet.from_pretrained('efficientnet-b0', num_classes=1)
        checkpoint = torch.load('/home/vortex/api-deepfake/efficientNetFFPP.pth', map_location='cpu', weights_only=True)
        
        if 'state_dict' in checkpoint:
            model.load_state_dict(checkpoint['state_dict'], strict=False)
        else:
            model.load_state_dict(checkpoint, strict=False)
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = model.eval().to(device)
        logging.info(f"Model loaded on device: {device}")
        return model
    except Exception as e:
        logging.error(f"Model loading error: {str(e)}")
        return None

try:
    deepfake_model = load_model()
except Exception as e:
    logging.error(f"Failed to initialize model: {e}")
    deepfake_model = None

# API Endpoints
@app.post("/detect")
async def detect(
    video: UploadFile = File(...),
    audio: UploadFile = File(None)
):
    try:
        video_path = await save_file(video)
        audio_path = await save_file(audio) if audio else None
        
        results = {
            'deepfake': await analyze_video(video_path) if deepfake_model else {'error': 'Model unavailable'},
            'voice': aws.detect_voice_fraud(audio_path) if audio else None
        }
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            
        return results
        
    except Exception as e:
        logging.error(f"Detection failed: {str(e)}")
        raise HTTPException(500, detail=str(e))

# Helper Functions
async def analyze_video(path: str) -> dict:
    if not deepfake_model:
        return {'error': 'Model unavailable'}
    
    device = next(deepfake_model.parameters()).device
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
                frame = cv2.resize(frame, (380, 380))
                tensor = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float() / 255.0
                tensor = tensor.to(device)
                
                with torch.no_grad():
                    pred = torch.sigmoid(deepfake_model(tensor)).item()
                    predictions.append(pred)
                    
            frame_count += 1
        
        return {
            'risk_score': float(np.mean(predictions)) if predictions else 0.5,
            'frames_analyzed': len(predictions)
        }
    finally:
        cap.release()

async def save_file(file: UploadFile) -> str:
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            content = await file.read()
            f.write(content)
            return f.name
    except Exception as e:
        logging.error(f"File save error: {str(e)}")
        raise HTTPException(status_code=500, detail="File processing failed")

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model_loaded": deepfake_model is not None,
        "aws_configured": all(key in os.environ for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)