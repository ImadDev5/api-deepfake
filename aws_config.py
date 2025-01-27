# aws_config.py
import uuid

import boto3
import os
from dotenv import load_dotenv
from botocore.config import Config
import logging
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSConfiguration:
    def __init__(self):
        load_dotenv()
        self.secret_cache = SecretCache(SecretCacheConfig())
        self._validate_environment()
        self._clients = {}

    def _validate_environment(self):
        """Validate required environment variables"""
        required_vars = ['AWS_REGION', 'AWS_SECRET_NAME']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    def _get_secrets(self):
        """Retrieve secrets from AWS Secrets Manager"""
        try:
            secret_string = self.secret_cache.get_secret_string(os.getenv('AWS_SECRET_NAME'))
            return json.loads(secret_string)
        except Exception as e:
            logger.error(f"Failed to retrieve secrets: {str(e)}")
            raise

    def get_client(self, service_name: str) -> boto3.client:
        """Get AWS service client with proper configuration"""
        if service_name not in self._clients:
            secrets = self._get_secrets()
            
            config = Config(
                connect_timeout=5,
                retries={'max_attempts': 3},
                signature_version='s3v4' if service_name == 's3' else None,
                read_timeout=60,
                region_name=os.getenv('AWS_REGION')
            )

            self._clients[service_name] = boto3.client(
                service_name,
                aws_access_key_id=secrets['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=secrets['AWS_SECRET_ACCESS_KEY'],
                region_name=os.getenv('AWS_REGION'),
                config=config
            )

        return self._clients[service_name]

    def get_all_clients(self) -> dict:
        """Initialize and return all required AWS service clients"""
        services = ['rekognition', 'comprehend', 'transcribe', 's3', 'frauddetector']
        return {service: self.get_client(service) for service in services}

aws_config = AWSConfiguration()