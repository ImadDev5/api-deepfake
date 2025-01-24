import boto3
import uuid
import time
import os
import requests
import logging
from botocore.exceptions import ClientError
from botocore.client import Config
from pydub import AudioSegment
from dotenv import load_dotenv
from constants import PHISHING_KEYWORDS, FRAUD_PATTERNS

load_dotenv()
logger = logging.getLogger('AWS-Utils')

class AWSServices:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION'),
            config=Config(signature_version='s3v4')
        )
        self.transcribe = boto3.client('transcribe')
        self.comprehend = boto3.client('comprehend')
        self.fraud_detector = boto3.client('frauddetector')
        self.sns = boto3.client('sns')

    # Voice Fraud Detection
    def detect_voice_fraud(self, audio_path: str) -> dict:
        try:
            wav_path = self._convert_to_wav(audio_path)
            s3_key = f"audio/{uuid.uuid4()}.wav"
            
            self.s3.upload_file(wav_path, os.getenv('AWS_S3_BUCKET'), s3_key)
            
            transcript = self._transcribe_audio(s3_key)
            sentiment = self.comprehend.detect_sentiment(Text=transcript, LanguageCode='en')
            
            risk_score = self._calculate_risk(transcript, sentiment)
            
            return {
                'risk_score': min(risk_score, 1.0),
                'is_fraud': risk_score > 0.7,
                'transcript': transcript,
                'sentiment': sentiment['Sentiment'],
                'flagged_keywords': self._find_phishing_terms(transcript)
            }

        except ClientError as e:
            logger.error(f"AWS Error: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}

    # Spam Call Analysis
    def analyze_call(self, metadata: dict) -> dict:
        risk_factors = {
            'short_duration': metadata.get('duration', 0) < 10,
            'hidden_number': metadata.get('caller_id', '') == 'hidden',
            'high_frequency': metadata.get('call_count', 0) > 5
        }
        
        risk_score = sum([0.3 for factor in risk_factors.values() if factor])
        return {
            'risk_score': min(risk_score, 1.0),
            'risk_factors': risk_factors
        }

    # Transaction Monitoring
    def monitor_transaction(self, user_id: str, amount: float):
        try:
            response = self.fraud_detector.get_event_prediction(
                detectorId='financial_fraud',
                eventId=str(uuid.uuid4()),
                eventVariables={
                    'user_id': user_id,
                    'amount': str(amount),
                    'transaction_type': 'VKYC_VERIFIED'
                }
            )
            return response['ruleResults']
        except ClientError as e:
            logger.error(f"Fraud detection error: {e}")
            return {'error': 'Transaction monitoring failed'}

    # Helper methods
    def _convert_to_wav(self, audio_path: str) -> str:
        if audio_path.endswith('.wav'):
            return audio_path
        audio = AudioSegment.from_file(audio_path)
        wav_path = f"{os.path.splitext(audio_path)[0]}.wav"
        audio.export(wav_path, format="wav")
        return wav_path

    def _transcribe_audio(self, s3_key: str) -> str:
        job_name = f"fraud_job_{uuid.uuid4().hex[:32]}"
        self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{os.getenv("AWS_S3_BUCKET")}/{s3_key}'},
            MediaFormat='wav',
            LanguageCode='en-IN'
        )
        
        for _ in range(30):  # 3 min timeout
            status = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(6)
            
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
            raise Exception("Transcription failed")
            
        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        return requests.get(transcript_uri).json()['results']['transcripts'][0]['transcript']

    def _calculate_risk(self, transcript: str, sentiment: dict) -> float:
        keyword_risk = sum(1 for kw in PHISHING_KEYWORDS if kw.lower() in transcript.lower()) / len(PHISHING_KEYWORDS)
        sentiment_risk = 0.2 if sentiment['Sentiment'] == 'NEGATIVE' else 0
        pattern_risk = any(all(p in transcript.lower() for p in pat) for pat in FRAUD_PATTERNS.values())
        return keyword_risk + sentiment_risk + (0.3 if pattern_risk else 0)

    def _find_phishing_terms(self, transcript: str) -> list:
        return [kw for kw in PHISHING_KEYWORDS if kw.lower() in transcript.lower()]