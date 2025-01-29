import uuid
from datetime import datetime
import logging
from collections import defaultdict
import boto3
from config import settings
from models import TransactionData

logger = logging.getLogger('TransactionMonitor')

class TransactionMonitor:
    def __init__(self):
        try:
            self.fraud_detector = boto3.client(
                'frauddetector',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            logger.info("Transaction Monitor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Fraud Detector: {str(e)}")
            raise

    def analyze_transaction(self, user_id: str, amount: float, metadata: dict) -> dict:
        """
        Analyze a single transaction using AWS Fraud Detector.
        """
        try:
            event_id = str(uuid.uuid4())
            response = self.fraud_detector.get_event_prediction(
                detectorId='transaction_fraud_detector',  # Replace with your detector ID
                eventId=event_id,
                eventTypeName='transaction',
                eventTimestamp=datetime.now().isoformat(),
                entities=[{
                    'entityType': 'customer',
                    'entityId': user_id
                }],
                eventVariables={
                    'amount': str(amount),
                    'currency': metadata.get('currency', 'INR'),
                    'user_risk_score': str(self._get_user_risk(user_id)),  # Convert to string
                    'device_type': metadata.get('device_type', 'unknown'),
                    'location': metadata.get('location', 'unknown')
                }
            )
            return {
                'risk_score': float(response['riskScore']),
                'reasons': [r.get('ruleId') for r in response.get('ruleResults', [])],
                'event_id': event_id
            }
        except Exception as e:
            logger.error(f"Transaction analysis failed: {str(e)}")
            return {
                'risk_score': 0.5,
                'reasons': [],
                'error': str(e)
            }

    def _get_user_risk(self, user_id: str) -> float:
        """
        Fetch historical risk score for the user (placeholder for now).
        """
        return 0.5  # Default risk score

    def detect_jamtara_patterns(self, transactions: list) -> dict:
        """
        Detect Jamtara-style scam patterns in a batch of transactions.
        """
        try:
            analysis = {
                'small_transactions': defaultdict(float),
                'locations': defaultdict(int),
                'timestamps': []
            }
            for tx in transactions:
                if tx['amount'] < 10000:  # Small transaction threshold
                    analysis['small_transactions'][tx['user_id']] += tx['amount']
                analysis['locations'][tx['location']] += 1
                analysis['timestamps'].append(tx['timestamp'])

            risk_score = self._calculate_jamtara_risk(analysis)
            return {
                'risk_score': risk_score,
                'analysis': analysis
            }
        except Exception as e:
            logger.error(f"Jamtara pattern detection failed: {str(e)}")
            return {
                'risk_score': 0.5,
                'error': str(e)
            }

    def _calculate_jamtara_risk(self, analysis: dict) -> float:
        """
        Calculate risk score based on Jamtara-style scam patterns.
        """
        risk = 0.0
        for user, total in analysis['small_transactions'].items():
            if total > 50000:  # Suspicious total small transactions
                risk += 0.4
        if len(analysis['locations']) > 2:  # Multiple locations
            risk += 0.3
        if self._detect_rapid_transactions(analysis['timestamps']):
            risk += 0.3
        return min(risk, 1.0)

    def _detect_rapid_transactions(self, timestamps: list) -> bool:
        """
        Detect rapid transactions within a short time frame.
        """
        if len(timestamps) < 3:
            return False
        timestamps.sort()
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
        return any(diff < 60 for diff in time_diffs)  # Transactions within 60 seconds

    def submit_feedback(self, feedback_data: dict) -> dict:
        """
        Submit user-reported suspicious transactions for further analysis.
        """
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            bucket_name = settings.aws_s3_bucket
            feedback_key = f"feedback/{feedback_data['user_id']}_{datetime.now().isoformat()}.json"
            s3.put_object(
                Bucket=bucket_name,
                Key=feedback_key,
                Body=str(feedback_data),
                ContentType="application/json"
            )
            return {"status": "success", "message": "Feedback submitted successfully"}
        except Exception as e:
            logger.error(f"Feedback submission failed: {str(e)}")
            return {"status": "error", "message": str(e)}