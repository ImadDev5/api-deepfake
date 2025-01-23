from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
import cv2
import numpy as np
import logging
import os
import tempfile
from efficientnet_pytorch import EfficientNet
from aws_utils import AWSServices
from liveness_utils import LivenessDetector
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="DeepGuard", version="3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

aws = AWSServices()
liveness_detector = LivenessDetector()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    model = EfficientNet.from_pretrained('efficientnet-b4', num_classes=1)
    model.load_state_dict(torch.load('efficientNetFFPP.pth', map_location=device))
    model = model.to(device).eval()
except Exception as e:
    model = None
    logging.error(f"Model loading failed: {str(e)}")

@app.post("/detect")
async def detect_fraud(
    video: UploadFile = File(...),
    audio: UploadFile = File(None)
):
    try:
        video_path = await save_file(video)
        results = {}
        
        # Liveness Check
        results['liveness'] = liveness_detector.check_liveness(video_path)
        
        # Voice Analysis
        if audio:
            audio_path = await save_file(audio)
            results['voice'] = aws.detect_voice_fraud(audio_path)
            os.remove(audio_path)
        
        os.remove(video_path)
        return results
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

async def save_file(file: UploadFile) -> str:
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(await file.read())
        return f.name

def analyze_video(video_path: str) -> dict:
    cap = cv2.VideoCapture(video_path)
    predictions = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % int(os.getenv('FRAME_SKIP', 5)) == 0:
            frame = cv2.resize(frame, (380, 380))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            tensor = torch.from_numpy(frame).permute(2,0,1).float().unsqueeze(0)
            tensor = tensor.to(device)
            
            with torch.no_grad():
                pred = torch.sigmoid(model(tensor)).cpu().item()
                predictions.append(pred)
                
        frame_count += 1
    
    return {
        'risk_score': np.mean(predictions) if predictions else 0.5,
        'frames_analyzed': len(predictions)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "aws_configured": all(key in os.environ for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)