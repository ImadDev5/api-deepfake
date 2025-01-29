import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AWSConfig:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "ap-south-1")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )
        self.rekognition = boto3.client(
            "rekognition",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )
        self.transcribe = boto3.client(
            "transcribe",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )
        self.comprehend = boto3.client(
            "comprehend",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )
        self.fraud_detector = boto3.client(
            "frauddetector",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )
