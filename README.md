# DeepGuard: Deepfake Detection API 🔍

**Team Md Imaduddin** - Backend & AI/ML, AWS Integration & Deployment  
**Kazi Israr Mohammed** - Frontend & UI  

A REST API to detect deepfake risks in video/audio inputs using AI/ML models, integrated with a responsive frontend and deployed on AWS.

---

## Features ✨
- **Multimodal Analysis**: Detect anomalies in video (lip-sync, facial artifacts) and audio (voice cloning, synthetic speech).
- **Risk Scoring**: Combined risk score for deepfake likelihood (0-1 scale).
- **Keyword Flagging**: Identify suspicious keywords in transcripts (e.g., "account", "winner").
- **Sentiment Analysis**: Categorize audio sentiment (`NEUTRAL`, `POSITIVE`, `NEGATIVE`).
- **AWS Deployment**: Scalable cloud infrastructure with load balancing.

---

## Tech Stack 🛠️
| Component       | Tools                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Backend**     | FastAPI, OpenCV, Librosa, TensorFlow/PyTorch                          |
| **Frontend**    | React.js, Material-UI, Chart.js                                       |
| **AWS Services**| EC2, S3 (File Storage), CloudWatch (Logging), API Gateway             |
| **DevOps**      | Docker, GitHub Actions (CI/CD), NGINX (Reverse Proxy)                 |

---

## Setup 🚀

### Prerequisites
- Python 3.9+, Node.js 16+
- AWS CLI (for deployment)
- FFmpeg (for video processing)

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/deepguard.git
   cd deepguard
Backend Setup:

bash
Copy
cd api-deepfake
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt  # Include FastAPI, numpy, torch, etc.
Frontend Setup:

bash
Copy
cd ../frontend
npm install
Run Locally:

Backend:

bash
Copy
uvicorn main:app --reload --port 8000
Frontend:

bash
Copy
npm start
API Documentation 📄
POST /detect
Analyze video/audio files for deepfake indicators.

Example Request:

bash
Copy
curl -X POST http://localhost:8000/detect \
  -F "video=@interview.mp4" \
  -F "audio=@interview.wav"
Example Response:

json
Copy
{
  "deepfake": {
    "risk_score": 0.72,
    "frames_analyzed": 120,
    "flagged_artifacts": ["lip_sync_mismatch", "unnatural_eye_blink"]
  },
  "voice": {
    "risk_score": 0.18,
    "is_fraud": false,
    "transcript": "Please share your bank account details...",
    "sentiment": "NEGATIVE",
    "flagged_keywords": ["bank account"]
  }
}
Edge Cases:

Video-only analysis:

bash
Copy
curl -X POST http://localhost:8000/detect -F "video=@test.mp4"
Audio-only analysis:

bash
Copy
curl -X POST http://localhost:8000/detect -F "audio=@test.wav"
Project Status 📌
Current (Q3 2023)
✅ Completed

Core deepfake detection model (ResNet-50 + LSTM hybrid).

Basic React frontend dashboard.

AWS EC2 deployment pipeline.

🚧 In Progress

Real-time video streaming analysis.

User authentication (JWT integration).

Future Goals 🎯
Mobile Integration: Flutter app for on-device analysis.

Blockchain Audit Trails: Store verified media hashes on Ethereum.

Globalization: Support for 10+ languages (Hindi, Mandarin, Arabic).

Enterprise Tier: Slack/MS Teams bot for corporate phishing prevention.

Architecture Overview 🏗️
plaintext
Copy
User → React Frontend → AWS API Gateway → FastAPI (EC2) → AI Models → S3 Storage
                               ↑
                          CloudWatch (Logs)
Contributing 🤝
Fork the repository.

Create a feature branch: git checkout -b feature/your-idea.

Submit a PR with tests and documentation.

Follow the Code of Conduct.

License 📜
MIT License. See LICENSE.

Acknowledgments 🌟
OpenAI Whisper (transcription baseline).

AWS AI/ML Scholarships for computational resources.
AWS for providing cloud services.

PyTorch community for pre-trained models.

FastAPI for building a high-performance backend.
