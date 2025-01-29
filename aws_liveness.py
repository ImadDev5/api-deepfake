import boto3
import os
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger("AWSLiveness")

class AWSLiveness:
    def __init__(self):
        self.client = boto3.client(
            "rekognition",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )

def validate_liveness(self, video_path: str) -> dict:
    try:
        bucket_name = os.getenv("AWS_S3_BUCKET")
        video_key = f"videos/{os.path.basename(video_path)}"
        self.s3.upload_file(video_path, bucket_name, video_key)
        response = self.client.detect_faces(
            Image={"S3Object": {"Bucket": bucket_name, "Name": video_key}},
            Attributes=["ALL"]
        )
        if not response.get("FaceDetails"):
            return {"error": "No faces detected in the video"}
        confidence = response["FaceDetails"][0]["Confidence"]
        is_live = response["FaceDetails"][0]["Smile"]["Value"]
        return {"confidence": confidence, "is_live": is_live}
    except ClientError as e:
        logger.error(f"Liveness validation failed: {e}")
        return {"error": str(e)}

    def compare_faces(self, video_path: str, id_card_path: str) -> dict:
        try:
            bucket_name = os.getenv("AWS_S3_BUCKET")
            video_key = f"videos/{os.path.basename(video_path)}"
            id_card_key = f"images/{os.path.basename(id_card_path)}"
            self.s3.upload_file(video_path, bucket_name, video_key)
            self.s3.upload_file(id_card_path, bucket_name, id_card_key)
            response = self.client.compare_faces(
                SourceImage={"S3Object": {"Bucket": bucket_name, "Name": id_card_key}},
                TargetImage={"S3Object": {"Bucket": bucket_name, "Name": video_key}}
        )
            if not response.get("FaceMatches"):
                return {"similarity": 0, "is_match": False}
            similarity = response["FaceMatches"][0]["Similarity"]
            return {"similarity": similarity, "is_match": similarity > 80}
        except ClientError as e:
            logger.error(f"Face comparison failed: {e}")
            return {"error": str(e)}