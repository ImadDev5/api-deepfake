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
        self.rekognition = boto3.client('rekognition', config=Config(signature_version='s3v4'))
        self.s3 = boto3.client('s3')

    def create_session(self) -> dict:
        try:
            response = self.rekognition.create_face_liveness_session()
            return {
                'session_id': response['SessionId'],
                'region': self.region
            }
        except ClientError as e:
            logger.error(f"Session creation failed: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}

    async def verify_session(self, session_id: str) -> dict:
        try:
            response = self.rekognition.get_face_liveness_session_results(SessionId=session_id)
            return {
                'confidence': response['Confidence'],
                'is_live': response['Status'] == 'LIVE',
                'session_id': session_id
            }
        except ClientError as e:
            logger.error(f"Verification failed: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}

    def full_vkyc_check(self, session_id: str, id_card: str) -> dict:
        try:
            # 1. Liveness verification
            liveness = self.verify_session(session_id)
            
            # 2. ID document matching
            id_match = self.rekognition.compare_faces(
                SourceImage={'S3Object': {'Bucket': os.getenv('S3_BUCKET'), 'Name': id_card}},
                TargetImage={'S3Object': {'Bucket': os.getenv('S3_BUCKET'), 'Name': f'sessions/{session_id}/frame.jpg'}}
            )
            
            # 3. Lip sync analysis
            lipsync = self.rekognition.start_lip_sync_analysis(
                Video={'S3Object': {'Bucket': os.getenv('S3_BUCKET'), 'Name': f'sessions/{session_id}/video.mp4'}}
            )
            
            return {
                'liveness': liveness,
                'id_match_confidence': id_match['FaceMatches'][0]['Similarity'] if id_match['FaceMatches'] else 0,
                'lipsync_valid': lipsync['Status'] == 'VALID'
            }
        except ClientError as e:
            logger.error(f"VKYC failed: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}