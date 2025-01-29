import boto3
import os
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger("FeedbackService")

class FeedbackService:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
        self.bucket_name = os.getenv("AWS_FEEDBACK_BUCKET", "fraud-feedback")

    def submit_feedback(self, feedback_data: dict) -> dict:
        """
        Submits user feedback to S3 for later analysis and training improvements.
        Args:
            feedback_data (dict): Feedback details such as user ID, type of fraud, etc.
        Returns:
            dict: Status of feedback submission.
        """
        try:
            feedback_key = f"feedback/{feedback_data['user_id']}_{feedback_data['timestamp']}.json"
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=feedback_key,
                Body=str(feedback_data),
                ContentType="application/json",
            )
            return {"status": "success", "message": "Feedback submitted successfully"}
        except ClientError as e:
            logger.error(f"Feedback submission failed: {e}")
            return {"status": "error", "message": str(e)}
