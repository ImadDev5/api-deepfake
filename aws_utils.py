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
        self.transcribe = boto3.client(
            'transcribe',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.comprehend = boto3.client(
            'comprehend',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

    def _convert_to_wav(self, audio_path: str) -> str:
        try:
            if audio_path.endswith('.wav'):
                return audio_path
            audio = AudioSegment.from_file(audio_path)
            wav_path = f"{os.path.splitext(audio_path)[0]}.wav"
            audio.export(wav_path, format="wav")
            return wav_path
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            raise

    def detect_voice_fraud(self, audio_path: str) -> dict:
        try:
            wav_path = self._convert_to_wav(audio_path)
            s3_key = f"audio/{uuid.uuid4()}.wav"
            
            self.s3.upload_file(
                wav_path,
                os.getenv('AWS_S3_BUCKET'),
                s3_key,
                ExtraArgs={'ContentType': 'audio/wav'}
            )

            job_name = f"fraud_job_{uuid.uuid4().hex[:32]}"
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f's3://{os.getenv("AWS_S3_BUCKET")}/{s3_key}'},
                MediaFormat='wav',
                LanguageCode='en-IN'
            )

            start_time = time.time()
            while time.time() - start_time < 300:
                status = self.transcribe.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                if job_status in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(10)

            if job_status == 'FAILED':
                return {'error': 'Transcription failed'}

            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            response = requests.get(transcript_uri)
            response.raise_for_status()
            transcript = response.json()['results']['transcripts'][0]['transcript']

            sentiment = self.comprehend.detect_sentiment(Text=transcript, LanguageCode='en')
            entities = self.comprehend.detect_entities(Text=transcript, LanguageCode='en')

            fraud_keywords = ['OTP', 'KYC', 'password', 'block', 'suspend']
            fraud_score = sum(1 for kw in fraud_keywords if kw.lower() in transcript.lower()) / len(fraud_keywords)
            fraud_score += 0.2 if sentiment['Sentiment'] == 'NEGATIVE' else 0

            return {
                'risk_score': min(fraud_score, 1.0),
                'is_fraud': fraud_score > 0.7,
                'transcript': transcript,
                'sentiment': sentiment['Sentiment'],
                'entities': [e['Text'] for e in entities['Entities']]
            }

        except ClientError as e:
            logger.error(f"AWS Error: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}
        except Exception as e:
            logger.error(f"Voice analysis failed: {str(e)}")
            return {'error': str(e)}