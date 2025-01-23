import boto3
import os
import logging
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('AWS-Liveness')

class AWSLivenessDetector:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'ap-south-1')
        self.client = boto3.client(
            'rekognition',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.region,
            config=Config(signature_version='s3v4')
        )

    def create_session(self) -> dict:
        """Create liveness session for frontend"""
        try:
            response = self.client.create_face_liveness_session()
            return {
                'session_id': response['SessionId'],
                'region': self.region
            }
        except ClientError as e:
            logger.error(f"Session creation failed: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}

    async def verify_session(self, session_id: str) -> dict:
        """Verify liveness results"""
        try:
            response = self.client.get_face_liveness_session_results(
                SessionId=session_id
            )
            return {
                'confidence': response['Confidence'],
                'is_live': response['Status'] == 'LIVE'
            }
        except ClientError as e:
            logger.error(f"Verification failed: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}