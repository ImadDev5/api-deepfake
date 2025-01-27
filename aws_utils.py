import boto3
import uuid
import time
import os
import logging
from botocore.exceptions import ClientError
from botocore.config import Config
from pydub import AudioSegment
import requests
from constants import PHISHING_KEYWORDS, FRAUD_PATTERNS
from indic_transliteration import sanscript
from config import settings

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AWSServices:
    def __init__(self):
        """Initialize AWS clients with proper configuration"""
        try:
            self._clients = {}
            self.stream_arn = settings.stream_arn
            
            # Validate required settings
            if not all([settings.aws_access_key_id, settings.aws_secret_access_key, 
                       settings.aws_region, settings.aws_s3_bucket]):
                raise ValueError("Missing required AWS configuration")
                
        except Exception as e:
            logger.error(f"AWS client initialization failed: {str(e)}")
            raise

    def _get_client(self, service_name: str) -> boto3.client:
        """Get or create an AWS client with proper configuration"""
        if service_name not in self._clients:
            config = Config(
                connect_timeout=settings.connect_timeout,
                retries={'max_attempts': settings.max_retries},
                signature_version='s3v4' if service_name == 's3' else None
            )

            self._clients[service_name] = boto3.client(
                service_name,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                config=config
            )
        return self._clients[service_name]

    @property
    def s3(self):
        return self._get_client('s3')

    @property
    def transcribe(self):
        return self._get_client('transcribe')

    @property
    def comprehend(self):
        return self._get_client('comprehend')

    def upload_to_s3(self, file_path: str) -> str:
        """Upload file to S3 and return the S3 URI"""
        try:
            file_name = os.path.basename(file_path)
            s3_key = f"audio/{uuid.uuid4()}/{file_name}"
            
            self.s3.upload_file(
                file_path,
                settings.aws_s3_bucket,
                s3_key
            )
            
            return f"s3://{settings.aws_s3_bucket}/{s3_key}"
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise

    def detect_voice_fraud(self, audio_path: str) -> dict:
        """Main fraud detection workflow"""
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Convert to WAV if needed
            wav_path = self._convert_to_wav(audio_path)
            
            # Upload to S3
            s3_uri = self.upload_to_s3(wav_path)
            
            # Process audio
            transcript = self._transcribe_audio(s3_uri)

            result = {
                'risk_score': 0.0,
                'transcript': '',
                'sentiment': 'NEUTRAL',
                'flagged_keywords': [],
                'audio_uri': s3_uri
            }

            if transcript:
                sentiment = self.comprehend.detect_sentiment(
                    Text=transcript,
                    LanguageCode='hi' if self._is_hindi(transcript) else 'en'
                )

                result.update({
                    'risk_score': self._calculate_risk(transcript, sentiment),
                    'transcript': transcript,
                    'sentiment': sentiment['Sentiment'],
                    'flagged_keywords': self._find_phishing_terms(transcript)
                })

            # Cleanup
            if wav_path != audio_path:
                os.remove(wav_path)

            return result

        except Exception as e:
            logger.error(f"Voice fraud detection failed: {str(e)}")
            return {
                'error': str(e),
                'risk_score': 0.5,
                'transcript': '',
                'sentiment': 'NEUTRAL',
                'audio_uri': None
            }

    def _transcribe_audio(self, s3_uri: str) -> str:
        """Transcribe audio file using Amazon Transcribe"""
        try:
            job_name = f"transcribe_job_{uuid.uuid4().hex}"
            
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': s3_uri},
                MediaFormat='wav',
                LanguageCode='hi-IN',
                Settings={
                    'ShowSpeakerLabels': True,
                    'MaxSpeakerLabels': 2
                }
            )

            # Wait for completion
            while True:
                status = self.transcribe.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                if job_status in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(5)

            if job_status == 'COMPLETED':
                transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                transcript_response = requests.get(transcript_uri)
                transcript_data = transcript_response.json()
                return transcript_data['results']['transcripts'][0]['transcript']
            else:
                logger.error(f"Transcription job failed: {status['TranscriptionJob'].get('FailureReason', 'Unknown error')}")
                return None

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return None

    def _calculate_risk(self, transcript: str, sentiment: dict) -> float:
        """Calculate risk score based on transcript and sentiment"""
        risk_score = 0.0

        # Check for phishing keywords
        for keyword in PHISHING_KEYWORDS:
            if keyword.lower() in transcript.lower():
                risk_score += 0.2

        # Check for fraud patterns
        for pattern, phrases in FRAUD_PATTERNS.items():
            for phrase in phrases:
                if phrase.lower() in transcript.lower():
                    risk_score += 0.3

        # Adjust risk score based on sentiment
        if sentiment['Sentiment'] == 'NEGATIVE':
            risk_score += 0.2
        elif sentiment['Sentiment'] == 'POSITIVE':
            risk_score -= 0.1

        return min(max(risk_score, 0.0), 1.0)

    def _convert_to_wav(self, audio_path: str) -> str:
        """Convert audio file to WAV format if needed"""
        try:
            if audio_path.lower().endswith('.wav'):
                return audio_path

            sound = AudioSegment.from_file(audio_path)
            wav_path = f"{os.path.splitext(audio_path)[0]}_converted.wav"
            sound.export(wav_path, format="wav", parameters=["-ar", "16000"])
            return wav_path
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            raise ValueError("Unsupported audio format") from e

    def _find_phishing_terms(self, transcript: str) -> list:
        """Find phishing terms in transcript"""
        return [keyword for keyword in PHISHING_KEYWORDS 
                if keyword.lower() in transcript.lower()]

    def _is_hindi(self, text: str) -> bool:
        """Check if text is primarily Hindi"""
        try:
            devanagari_text = sanscript.transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)
            return len(devanagari_text.strip()) > 0
        except Exception as e:
            logger.error(f"Hindi detection failed: {str(e)}")
            return False