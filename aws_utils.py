import boto3
import uuid
import time
import os
import logging
from botocore.exceptions import ClientError
from botocore.config import Config
from pydub import AudioSegment
import requests  # Ensure this library is installed
from config import settings

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSServices:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
            config=Config(signature_version='s3v4')
        )
        self.transcribe = boto3.client('transcribe', region_name=settings.aws_region)
        self.comprehend = boto3.client('comprehend', region_name=settings.aws_region)
        self.fraud_detector = boto3.client('frauddetector', region_name=settings.aws_region)

    def detect_voice_fraud(self, audio_path: str) -> dict:
        try:
            wav_path = self._convert_to_wav(audio_path)
            s3_key = f"audio/{uuid.uuid4()}.wav"
            self.s3.upload_file(wav_path, settings.aws_s3_bucket, s3_key)
            transcript = self._transcribe_audio(s3_key)

        # Detect language using AWS Comprehend
            language_response = self.comprehend.detect_dominant_language(Text=transcript)
            dominant_language = language_response['Languages'][0]['LanguageCode']
            if dominant_language == 'hi':
            # Translate Hindi transcript to English for further analysis
                translate_client = boto3.client('translate', region_name=settings.aws_region)
                translation = translate_client.translate_text(
                    Text=transcript,
                    SourceLanguageCode='hi',
                    TargetLanguageCode='en'
                )
                transcript = translation['TranslatedText']

            sentiment = self.comprehend.detect_sentiment(Text=transcript, LanguageCode='en')
            risk_score = self._calculate_risk(transcript, sentiment)
            return {
                'risk_score': min(risk_score, 1.0),
                'is_fraud': risk_score > 0.7,
                'transcript': transcript,
                'language': dominant_language,
                'sentiment': sentiment['Sentiment'],
                'flagged_keywords': self._find_phishing_terms(transcript)
            }
        except ClientError as e:
            logger.error(f"AWS Error: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}

    def _convert_to_wav(self, audio_path: str) -> str:
        """Convert audio file to WAV format if necessary."""
        if audio_path.endswith('.wav'):
            return audio_path
        try:
            audio = AudioSegment.from_file(audio_path)
            wav_path = f"{os.path.splitext(audio_path)[0]}.wav"
            audio.export(wav_path, format="wav")
            return wav_path
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            raise ValueError("Unsupported audio format") from e

    def _transcribe_audio(self, s3_key: str) -> str:
        """Transcribe audio using AWS Transcribe."""
        job_name = f"fraud_job_{uuid.uuid4().hex[:32]}"
        try:
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f's3://{settings.aws_s3_bucket}/{s3_key}'},
                MediaFormat='wav',
                LanguageCode='en-IN'
            )
            for _ in range(30):  # 3-minute timeout (6 seconds per iteration)
                status = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                if job_status in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(6)
            if job_status == 'FAILED':
                raise Exception("Transcription failed")
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            response = requests.get(transcript_uri)
            return response.json()['results']['transcripts'][0]['transcript']
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise

    def _calculate_risk(self, transcript: str, sentiment: dict) -> float:
        """Calculate fraud risk score based on keywords, sentiment, and patterns."""
        keyword_risk = sum(1 for kw in settings.PHISHING_KEYWORDS if kw.lower() in transcript.lower()) / len(settings.PHISHING_KEYWORDS)
        sentiment_risk = 0.2 if sentiment['Sentiment'] == 'NEGATIVE' else 0
        pattern_risk = any(all(p in transcript.lower() for p in pat) for pat in settings.FRAUD_PATTERNS.values())
        return keyword_risk + sentiment_risk + (0.3 if pattern_risk else 0)

    def _find_phishing_terms(self, transcript: str) -> list:
        """Identify phishing terms in the transcript."""
        return [kw for kw in settings.PHISHING_KEYWORDS if kw.lower() in transcript.lower()]