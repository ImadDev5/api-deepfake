import uuid
from datetime import datetime
import logging
import os
import boto3
from collections import defaultdict
from config import settings

logger = logging.getLogger('TransactionMonitor')

class TransactionMonitor:
    def __init__(self):
        """Initialize AWS Fraud Detector client"""
        try:
            self.fraud_detector = boto3.client(
                'frauddetector',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
        except Exception as e:
            logger.error(f"Failed to initialize Fraud Detector: {str(e)}")
            raise

    def analyze_transaction(self, user_id: str, amount: float, metadata: dict) -> dict:
        """Analyze a transaction for fraud risks"""
        try:
            event_id = str(uuid.uuid4())
            
            response = self.fraud_detector.get_event_prediction(
                detectorId='transaction_fraud_detector',
                eventId=event_id,
                eventTypeName='transaction',
                eventTimestamp=datetime.now().isoformat(),
                entities=[{
                    'entityType': 'customer',
                    'entityId': user_id
                }],
                eventVariables={
                    'amount': str(amount),
                    'currency': 'INR',
                    'user_risk_score': self._get_user_risk(user_id),
                    **metadata
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
        """Calculate user-specific risk score"""
        # This can be enhanced with actual user behavior analysis
        return 0.5  # Default risk score

    def detect_jamtara_patterns(self, transactions: list) -> dict:
        """Detect Jamtara-style fraud patterns"""
        try:
            analysis = {
                'small_transactions': defaultdict(float),
                'locations': defaultdict(int),
                'timestamps': []
            }

            for tx in transactions:
                # Small transaction accumulation
                if tx['amount'] < 10000:
                    analysis['small_transactions'][tx['user_id']] += tx['amount']
                
                # Geographic analysis
                analysis['locations'][tx['location']] += 1
                
                # Time analysis
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
        """Calculate risk score based on Jamtara patterns"""
        risk = 0.0
        
        # Small transaction accumulation
        for user, total in analysis['small_transactions'].items():
            if total > 50000:
                risk += 0.4
                
        # Multiple locations
        if len(analysis['locations']) > 2:
            risk += 0.3
            
        # Rapid transactions
        if self._detect_rapid_transactions(analysis['timestamps']):
            risk += 0.3
            
        return min(risk, 1.0)

    def _detect_rapid_transactions(self, timestamps: list) -> bool:
        """Detect rapid transaction patterns"""
        if len(timestamps) < 3:
            return False
            
        time_diffs = [
            (timestamps[i+1] - timestamps[i]).total_seconds()
            for i in range(len(timestamps)-1)
        ]
        
        return any(diff < 60 for diff in time_diffs)