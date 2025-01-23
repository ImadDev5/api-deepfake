import boto3
import uuid
import time
import requests
import os
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

class AWSServices:
    def __init__(self):
        aws_config = Config(
            region_name=os.getenv('AWS_REGION'),
            retries={'max_attempts': 3, 'mode': 'standard'},
            signature_version='s3v4'
        )
        
        self.s3 = boto3.client(
            's3',
            config=aws_config,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        self.rekognition = boto3.client(
            'rekognition',
            config=aws_config,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        self.transcribe = boto3.client(
            'transcribe',
            config=aws_config,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        self.comprehend = boto3.client(
            'comprehend',
            config=aws_config,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

    def detect_voice_fraud(self, audio_path: str) -> dict:
        try:
            object_key = f"audio/{uuid.uuid4()}.wav"
            self.s3.upload_file(
                audio_path,
                os.getenv('AWS_S3_BUCKET'),
                object_key,
                ExtraArgs={'ContentType': 'audio/wav'}
            )
            
            job_name = f"fraud_job_{uuid.uuid4()}"
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f's3://{os.getenv("AWS_S3_BUCKET")}/{object_key}'},
                MediaFormat='wav',
                LanguageCode='en-IN'
            )
            
            max_wait = 300
            start_time = time.time()
            while time.time() - start_time < max_wait:
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
            transcript_text = response.json()['results']['transcripts'][0]['transcript']
            
            sentiment = self.comprehend.detect_sentiment(
                Text=transcript_text,
                LanguageCode='en'
            )
            
            phishing_terms = ["OTP", "KYC", "block", "suspend", "password"]
            fraud_score = sum(
                1 for term in phishing_terms 
                if term.lower() in transcript_text.lower()
            ) / len(phishing_terms)
            
            negative_bias = 0.5 if sentiment['Sentiment'] == 'NEGATIVE' else 0.0
            return {
                'risk_score': min(fraud_score + negative_bias, 1.0),
                'transcript': transcript_text,
                'is_fraud': (fraud_score + negative_bias) > 0.7
            }
            
        except ClientError as e:
            return {'error': str(e)}
        except Exception as e:
            return {'error': str(e)}