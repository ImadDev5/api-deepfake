# DeepGuard 2.0: Advanced Fraud Detection System

DeepGuard 2.0 is a cutting-edge fraud detection system that leverages AWS services, deepfake detection models, and transaction monitoring to identify and prevent fraudulent activities. It includes features such as liveness checks, video KYC verification, deepfake detection, and voice fraud analysis.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

DeepGuard 2.0 is designed to combat modern fraud techniques, including deepfakes, voice phishing (vishing), and Jamtara-style scams. The system integrates AWS Fraud Detector, Rekognition, Transcribe, and Comprehend to provide real-time risk analysis and fraud detection.

---

## Features

- **Liveness Check**: Ensures the user is physically present during transactions using AWS Rekognition.
- **Video KYC Verification**: Matches the user's face in a video with their ID card image.
- **Deepfake Detection**: Analyzes videos to detect deepfake content using a pre-trained EfficientNet model.
- **Voice Fraud Analysis**: Detects phishing keywords, sentiment, and suspicious patterns in audio recordings.
- **Transaction Monitoring**: Analyzes individual transactions and detects suspicious patterns like rapid small transactions or multiple locations.
- **Feedback Submission**: Allows users to report suspicious transactions for further analysis.

---

## Technologies Used

- **Backend Framework**: FastAPI
- **Machine Learning Models**:
  - EfficientNet-B4 (Deepfake Detection)
  - AWS Rekognition (Face Matching, Liveness Check)
  - AWS Transcribe (Audio Transcription)
  - AWS Comprehend (Sentiment Analysis)
- **Cloud Services**:
  - AWS S3 (File Storage)
  - AWS Fraud Detector (Transaction Risk Analysis)
- **Frontend**: HTML + JavaScript (AWS Amplify Integration)
- **Dependencies**: PyTorch, Boto3, Pydantic, OpenCV, Pillow

---

## Setup Instructions

### Prerequisites

1. **Python 3.8+**: Ensure Python is installed on your system.
2. **AWS Account**: Create an AWS account and configure IAM roles with permissions for:
   - Rekognition
   - S3
   - Transcribe
   - Comprehend
   - Fraud Detector
3. **Deepfake Model**: Download the pre-trained EfficientNet model (`efficientNetFFPP.pth`) and place it in the project root directory.

### Installation

1. Clone the repository:
   ```bash
   https://github.com/ImadDev5/api-deepfake.git
   cd api-deepfake

2. Create a virtual environment:
   python3 -m venv myenv
   source myenv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Configure environment variables:
Rename .env.example to .env and update the following:
   AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=ap-south-1
AWS_S3_BUCKET=your-s3-bucket-name
COGNITO_CLIENT_ID=your-cognito-client-id
COGNITO_USER_POOL_ID=your-user-pool-id
COGNITO_IDENTITY_POOL_ID=your-identity-pool-id



5. Start the server:
  uvicorn main:app --reload --host 0.0.0.0 --port 8000


Open the frontend in your browser:
Navigate to frontend/index.html.


API Endpoints
/health
GET
Health check endpoint.
/detect
POST
Detect deepfakes and voice fraud.
/vkyc
POST
Perform Video KYC verification.
/analyze-transaction
POST
Analyze individual transactions for fraud.
/detect-jamtara
POST
Detect Jamtara-style scam patterns.

Project Structure
deepguard/
├── frontend/               # Frontend files (HTML, JS)
│   ├── index.html          # Main frontend page
│   └── liveness.js         # Liveness check integration
├── efficientNetFFPP.pth    # Pre-trained deepfake detection model
├── main.py                 # FastAPI backend entry point
├── aws_liveness.py         # AWS Liveness Detector utility
├── aws_utils.py            # AWS service integrations
├── config.py               # Configuration settings
├── constants.py            # Constants for phishing keywords and fraud patterns
├── feedback.py             # Feedback submission service
├── liveness_utils.py       # Liveness check utilities
├── transaction_monitor.py  # Transaction monitoring logic
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation



Example Responses
Below are example requests and responses for each API endpoint.

1. Deepfake and Voice Fraud Detection (/detect)
Detects deepfakes in videos and voice fraud in audio recordings.

curl -X POST http://localhost:8000/detect \
-F "video=@test.mp4" \
-F "audio=@test.wav"

{
  "deepfake": {
    "risk_score": 0.85,
    "frames_analyzed": 120
  },
  "voice": {
    "risk_score": 0.9,
    "is_fraud": true,
    "transcript": "Please share your OTP immediately to claim your lottery prize.",
    "sentiment": "NEGATIVE",
    "flagged_keywords": ["OTP", "lottery", "claim"]
  }
}

Request:
curl -X POST http://localhost:8000/detect \
-F "video=@test.mp4" \
-F "audio=@test.wav"

Response:
{
  "deepfake": {
    "risk_score": 0.85,
    "frames_analyzed": 120
  },
  "voice": {
    "risk_score": 0.9,
    "is_fraud": true,
    "transcript": "Please share your OTP immediately to claim your lottery prize.",
    "sentiment": "NEGATIVE",
    "flagged_keywords": ["OTP", "lottery", "claim"]
  }
}

2. Video KYC Verification (/vkyc)
Performs face matching and liveness checks for Video KYC.

Request:
curl -X POST http://localhost:8000/vkyc \
-F "video=@test.mp4" \
-F "id_card=@id_card.jpeg"

Response:
{
  "liveness": {
    "confidence": 95.7,
    "status": "SUCCEEDED",
    "session_id": "abc123-def456"
  },
  "face_match": {
    "similarity": 92.3,
    "matched": true
  },
  "session_id": "abc123-def456"
}
Note; Repeat similar sections for /analyze-transaction, /detect-jamtara, and /health.

Contact
For questions or feedback, please contact:

Email : imaduddin.dev@gmail.com
GitHub : @ImadDev5

