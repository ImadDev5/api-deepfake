import boto3
import os
import logging
from botocore.client import Config
from botocore.exceptions import ClientError
from config import settings
import uuid
from PIL import Image
import cv2

logger = logging.getLogger('AWS-Liveness')

class AWSLivenessDetector:
    def __init__(self):
        try:
            self.region = settings.aws_region
            self.rekognition = boto3.client(
                'rekognition',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                config=Config(
                    signature_version='s3v4',
                    retries={'max_attempts': settings.max_retries},
                    connect_timeout=settings.connect_timeout
                )
            )
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                config=Config(
                    signature_version='s3v4',
                    retries={'max_attempts': settings.max_retries},
                    connect_timeout=settings.connect_timeout
                )
            )
            self.bucket_name = settings.aws_s3_bucket
            logger.info("AWS Liveness Detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise

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

    def get_session_results(self, session_id: str) -> dict:
        try:
            response = self.rekognition.get_face_liveness_session_results(
                SessionId=session_id
            )
            return {
                'confidence': response['Confidence'],
                'status': response['Status'],
                'session_id': session_id
            }
        except ClientError as e:
            logger.error(f"Failed to get session results: {e.response['Error']['Message']}")
            return {'error': e.response['Error']['Message']}

    def upload_to_s3(self, file_path: str, s3_key: str) -> str:
        try:
            self.s3.upload_file(
                file_path,
                self.bucket_name,
                s3_key
            )
            return f"s3://{self.bucket_name}/{s3_key}"
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise

    def _convert_to_jpeg(self, file_path: str) -> str:
        try:
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                return file_path
            img = Image.open(file_path)
            jpeg_path = f"{os.path.splitext(file_path)[0]}_converted.jpg"
            img.convert('RGB').save(jpeg_path, 'JPEG')
            return jpeg_path
        except Exception as e:
            logger.error(f"Image conversion failed: {str(e)}")
            raise ValueError("Unsupported image format") from e

    def _extract_frame_from_video(self, video_path: str) -> str:
        try:
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            if not ret:
                raise ValueError("Failed to extract frame from video")
            frame_path = f"{os.path.splitext(video_path)[0]}_frame.jpg"
            cv2.imwrite(frame_path, frame)
            cap.release()
            return frame_path
        except Exception as e:
            logger.error(f"Video frame extraction failed: {str(e)}")
            raise ValueError("Unsupported video format") from e

    def full_vkyc_check(self, session_id: str, id_card_path: str, video_path: str) -> dict:
        temp_files = []  # Track temporary files for cleanup
        try:
            # Convert ID card to JPEG if needed
            id_card_path = self._convert_to_jpeg(id_card_path)
            if id_card_path not in [id_card_path]:
                temp_files.append(id_card_path)

            # Extract frame from video
            video_frame_path = self._extract_frame_from_video(video_path)
            temp_files.append(video_frame_path)

            # Upload files to S3
            id_card_key = f"vkyc/{session_id}/id_card.jpg"
            video_frame_key = f"vkyc/{session_id}/frame.jpg"
            id_card_uri = self.upload_to_s3(id_card_path, id_card_key)
            video_frame_uri = self.upload_to_s3(video_frame_path, video_frame_key)

            # Get liveness results
            liveness_result = self.get_session_results(session_id)

            # Compare faces
            compare_response = self.rekognition.compare_faces(
                SourceImage={
                    'S3Object': {
                        'Bucket': self.bucket_name,
                        'Name': id_card_key
                    }
                },
                TargetImage={
                    'S3Object': {
                        'Bucket': self.bucket_name,
                        'Name': video_frame_key
                    }
                },
                SimilarityThreshold=80.0
            )

            result = {
                'liveness': liveness_result,
                'face_match': {
                    'similarity': compare_response['FaceMatches'][0]['Similarity']
                    if compare_response.get('FaceMatches') else 0,
                    'matched': len(compare_response.get('FaceMatches', [])) > 0
                },
                'session_id': session_id
            }

            return result

        except Exception as e:
            logger.error(f"VKYC check failed: {str(e)}")
            raise

        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                try:
                    if temp_file and os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temporary file {temp_file}: {str(e)}")