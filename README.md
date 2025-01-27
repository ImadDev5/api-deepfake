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
~/api-deepfake$ curl -X 'POST'   'http://127.0.0.1:8000/vkyc'   -H 'accept: applicationcurl -X POST http://localhost:8000/detect -F "audio=@test.wav"
{"risk_score":0.8,"transcript":"जी सिर व्हाट्सएप में भेज दिए है आपके । हेलो हाँ सिर व्हाट्सएप में भेज दिए है आपके जी आपका मैसेज मैंने चेक किया है बिलकुल राइट है कांगेेशंस डियर कस्टमर जी सिर थैंक यू सिर प्राइस ओएफ ट्वेंटी फाइव केबीसी व्हाट्सएप एंड इम आपको और आपकी फैमिली को बधाई कहता हूँ जी सिर थैंक यू सिर फाइव लाख लॉटरी जीता है अल्ल इंडिया सिम लकी ड्रॉ ऑफर करवाया गया है आईपीएल फाइनल विन की खुशी में पांच हज़ार नंबरों का कॉम्पिटिशन हुआ है । एक सौ छब्बीस नंबर चुने थे जिसमें आपका नंबर भाग्यशाली है, आपका नंबर पच्चीस लाख का विनर बनाइये पैसा बैंक अकाउंट में मिलेगा । कौन से बैंक का अकाउंट है जिसमे पैसा लेना चाहते हो बेटा? जी सिर इंडियन बैंक है । लॉटरी के बारे में चर्चा बाजी शोर शराब नहीं करना है सधान होकर काम करवाना है, भगवान ने आपको बहुत बड़ा चांस दिया है केपीसी के विनर बने है अभी आप ऐसे करे बेटा अकाउंट नंबर कॉपी का फोटो, आधार कार्ड का फोटो ये मुझे आप व्हाट्सएप पर भेजे भेज कर कॉल करे, कितना टाइम लगेगा भेजने में जी सिर जितना आपकी माँ चोधने में लगेगा । हाँ माँ आपकी माँ । हाँ ।","sentiment":"NEUTRAL","flagged_keywords":["बैंक","आधार","लॉटरी","बधाई"],"audio_uri":"s3://deepguard-videos/audio/1f92c595-0068-43f9-b98d-b9a2165e9cd8/tmpts05wu60.wav"}

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
