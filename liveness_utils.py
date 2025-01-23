import boto3
import os
import time
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

class LivenessDetector:
    def __init__(self):
        self.client = boto3.client(
            'rekognition',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION'),
            config=Config(signature_version='s3v4')
        )
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

    def check_liveness(self, video_path: str) -> dict:
        try:
            # Upload video to S3
            s3_key = f"liveness/{uuid.uuid4()}.mp4"
            self.s3.upload_file(
                video_path,
                os.getenv('AWS_S3_BUCKET'),
                s3_key,
                ExtraArgs={'ContentType': 'video/mp4'}
            )

            # Start face detection
            response = self.client.start_face_detection(
                Video={
                    'S3Object': {
                        'Bucket': os.getenv('AWS_S3_BUCKET'),
                        'Name': s3_key
                    }
                },
                FaceAttributes='ALL'
            )

            job_id = response['JobId']
            max_wait = 300  # 5 minutes
            start_time = time.time()

            while time.time() - start_time < max_wait:
                status = self.client.get_face_detection(JobId=job_id)
                if status['JobStatus'] in ['SUCCEEDED', 'FAILED']:
                    break
                time.sleep(10)

            if status['JobStatus'] == 'FAILED':
                return {'status': 'error', 'error': 'Face detection failed'}

            # Calculate liveness score
            face_details = status['Faces']
            if not face_details:
                return {'status': 'error', 'error': 'No faces detected'}

            liveness_score = sum(
                face['Face']['Confidence'] for face in face_details
            ) / len(face_details)

            return {
                'status': 'success',
                'score': liveness_score / 100,
                'is_live': liveness_score > 70
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}