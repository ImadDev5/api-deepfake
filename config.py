from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import logging
from logging.config import dictConfig

class Settings(BaseSettings):
    # Required AWS credentials
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "ap-south-1"
    aws_s3_bucket: str
    stream_arn: str
    
    # Cognito settings
    cognito_pool_id: str
    cognito_client_id: str
    cognito_user_pool_id: str
    cognito_identity_pool_id: str
    
    # Video processing settings
    frame_skip: int = 5
    video_size: int = 380
    
    # AWS client settings
    max_retries: int = 2
    connect_timeout: int = 5
    
    # Feature flags
    enable_hindi_support: bool = True
    enable_sentiment_analysis: bool = True
    
    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def configure_logging(self):
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": self.log_level
                }
            },
            "root": {
                "handlers": ["console"],
                "level": self.log_level
            }
        }
        dictConfig(logging_config)

@lru_cache()
def get_settings():
    settings = Settings()
    settings.configure_logging()
    return settings

settings = get_settings()