from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
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

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="DeepGuard", version="3.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Initialize AWS services
aws = AWSServices()
liveness_detector = AWSLivenessDetector()

# Load deepfake model
def load_model():
    try:
        model = EfficientNet.from_pretrained('efficientnet-b0', num_classes=1)
        checkpoint = torch.load('efficientNetFFPP.pth', map_location='cpu')
        
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
        raise

try:
    deepfake_model = load_model()
except Exception as e:
    logging.error(f"Failed to initialize model: {e}")
    deepfake_model = None

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend/index.html") as f:
        return HTMLResponse(content=f.read())

# Liveness detection endpoints
@app.post("/api/create-session")
async def create_session():
    return liveness_detector.create_session()

@app.post("/api/verify-session")
async def verify_session(session_id: str = Body(..., embed=True)):
    return await liveness_detector.verify_session(session_id)

# Existing deepfake detection endpoint
@app.post("/detect")
async def detect(
    video: UploadFile = File(...),
    audio: UploadFile = File(None)
):
    try:
        video_path = await save_file(video)
        results = {}

        # Deepfake analysis
        if deepfake_model is not None:
            results['deepfake'] = await analyze_video(video_path)
        else:
            results['deepfake_error'] = "Deepfake model not available"

        # Voice analysis
        audio_path = None
        if audio is not None:
            audio_path = await save_file(audio)
            voice_result = aws.detect_voice_fraud(audio_path)
            results['voice'] = voice_result

        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

        return results

    except Exception as e:
        logging.error(f"API error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def analyze_video(path: str) -> dict:
    if deepfake_model is None:
        return {'error': 'Model not initialized'}
    
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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model_loaded": deepfake_model is not None,
        "aws_configured": all(key in os.environ for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'])
    }

# Server startup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)