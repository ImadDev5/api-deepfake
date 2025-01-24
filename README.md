 DeepGuard: Combating Spam Calls, Deepfake Fraud, and VKYC Exploitation


DeepGuard is an AI-powered solution designed to detect and prevent spam calls, deepfake-based fraud, and exploitation of Video KYC (VKYC) systems in financial services. Built using **AWS services** and **PyTorch**, it provides real-time analysis of video and audio inputs to identify fraudulent activities.

---

## 🚀 Features

1. **Deepfake Detection**:
   - Analyzes video frames to detect manipulated facial features.
   - Provides a risk score indicating the likelihood of deepfake content.

2. **Voice Fraud Detection**:
   - Transcribes and analyzes audio for phishing attempts and scam keywords.
   - Detects sentiment and identifies flagged keywords (e.g., "OTP", "KYC").

3. **Real-Time Alerts**:
   - Sends alerts for suspicious activities (e.g., deepfake detected, phishing attempt).

4. **VKYC Integrity**:
   - Ensures the authenticity of Video KYC sessions using liveness detection and ID matching.

5. **GDPR Compliance**:
   - Anonymizes sensitive data to protect user privacy.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **AI/ML**: PyTorch, EfficientNet
- **AWS Services**: Rekognition, Transcribe, Comprehend, S3
- **Frontend**: HTML, JavaScript, AWS Amplify
- **Other Tools**: OpenCV, Pydub

---

## 📂 Project Structure
api-deepfake/
├── frontend/ # Frontend files
│ ├── index.html # Main interface
│ └── liveness.js # Liveness check logic
├── main.py # FastAPI backend
├── aws_utils.py # AWS service integrations
├── liveness_utils.py # VKYC and liveness detection
├── efficientNetFFPP.pth # Deepfake detection model
├── .env # Environment variables
└── README.md # This file

Copy

---

## 🎯 Problem Statement

DeepGuard addresses the growing threat of **spam calls**, **deepfake fraud**, and **VKYC exploitation** in financial services. It provides a comprehensive solution to:

- Detect and block spam calls using NLP and behavioral analysis.
- Identify deepfake videos in real-time during VKYC sessions.
- Monitor post-VKYC transactions for suspicious activities.

---

## 🏆 Success Metrics

- **Detection Accuracy**: >90% for deepfake and spam call detection.
- **Latency**: <2 seconds for real-time analysis.
- **Fraud Reduction**: >50% reduction in fraudulent VKYC approvals.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- AWS Account with required services enabled
- Node.js (for frontend)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/api-deepfake.git
   cd api-deepfake
Install Python dependencies:

bash
Copy
pip install -r requirements.txt
Set up AWS credentials in .env:

env
Copy
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
AWS_S3_BUCKET=your-bucket-name
Start the server:

bash
Copy
uvicorn main:app --reload
Access the frontend at http://localhost:8000.

🧪 Testing
API Endpoints
Deepfake Detection:

bash
Copy
curl -X POST http://localhost:8000/detect -F "video=@test.mp4" -F "audio=@test.wav"
VKYC Verification:

bash
Copy
curl -X POST http://localhost:8000/vkyc -H "Content-Type: application/json" -d '{"session_id": "your-session-id", "id_card": "s3://your-bucket/id-card.jpg"}'
Health Check:

bash
Copy
curl http://localhost:8000/health
📊 Example API Responses
Deepfake Detected
json
Copy
{
  "deepfake": {
    "risk_score": 0.85,
    "frames_analyzed": 120,
    "message": "High risk of deepfake detected!"
  },
  "voice": {
    "risk_score": 0.2,
    "is_fraud": false,
    "transcript": "Hello, this is your bank. Please verify your account details.",
    "sentiment": "NEUTRAL",
    "flagged_keywords": ["bank", "verify"]
  }
}
Legitimate Content
json
Copy
{
  "deepfake": {
    "risk_score": 0.12,
    "frames_analyzed": 90,
    "message": "Low risk of deepfake. Content appears legitimate."
  },
  "voice": {
    "risk_score": 0.05,
    "is_fraud": false,
    "transcript": "Thank you for choosing our service. Have a great day!",
    "sentiment": "POSITIVE",
    "flagged_keywords": []
  }
}
Voice Fraud Detected
json
Copy
{
  "deepfake": {
    "risk_score": 0.3,
    "frames_analyzed": 100,
    "message": "Low risk of deepfake."
  },
  "voice": {
    "risk_score": 0.9,
    "is_fraud": true,
    "transcript": "Your account has been blocked. Please share your OTP to unlock it.",
    "sentiment": "NEGATIVE",
    "flagged_keywords": ["blocked", "OTP"]
  }
}
🏅 Hackathon Submission
Key Highlights
Real-Time Detection: Analyzes video and audio inputs in <2 seconds.

AWS Integration: Leverages Rekognition, Transcribe, and Comprehend for scalable fraud detection.

GDPR Compliance: Ensures user data privacy through anonymization.

Future Work
Integrate with mobile banking apps for real-time fraud prevention.

Add multi-language support for voice analysis.

Implement blockchain for secure transaction logging.

👥 Team
Md Imaduddin - Backend & AI/ML, AWS Integration & Deployment

Kazi Israr Mohammed - Frontend & UI

📜 License
This project is licensed under the MIT License. See LICENSE for details.

🙏 Acknowledgments
AWS for providing cloud services.

PyTorch community for pre-trained models.

FastAPI for building a high-performance backend.
