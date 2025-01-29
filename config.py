from typing import Optional, Any
from pydantic_settings import BaseSettings
import logging
from logging.config import dictConfig
from functools import lru_cache
import torch
from constants import PHISHING_KEYWORDS, FRAUD_PATTERNS  # Import constants

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "ap-south-1"
    aws_s3_bucket: str
    stream_arn: str
    cognito_pool_id: str
    cognito_client_id: str
    cognito_user_pool_id: str
    cognito_identity_pool_id: str
    frame_skip: int = 5
    video_size: int = 380
    max_retries: int = 2
    connect_timeout: int = 5
    enable_hindi_support: bool = True
    enable_sentiment_analysis: bool = True
    log_level: str = "INFO"
    deepfake_model: Optional[Any] = None  # Dynamic deepfake model assignment
    PHISHING_KEYWORDS: list = PHISHING_KEYWORDS  # Add phishing keywords
    FRAUD_PATTERNS: dict = FRAUD_PATTERNS  # Add fraud patterns

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
                    "level": self.log_level,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": self.log_level,
            },
        }
        dictConfig(logging_config)


@lru_cache()
def get_settings():
    settings = Settings()
    settings.configure_logging()
    settings.deepfake_model = load_model()  # Dynamically assign the model
    return settings


def load_model():
    try:
        # Load the EfficientNet model architecture
        from efficientnet_pytorch import EfficientNet
        model = EfficientNet.from_pretrained("efficientnet-b4")
        # Modify the classifier layer to match the pre-trained weights
        num_features = model._fc.in_features
        model._fc = torch.nn.Linear(num_features, 1)  # Binary classification (real/fake)
        # Load the pre-trained weights
        checkpoint_path = "efficientNetFFPP.pth"
        checkpoint = torch.load(checkpoint_path, map_location="cpu")
        # Handle potential mismatches in state_dict keys
        if "state_dict" in checkpoint:
            model.load_state_dict(checkpoint["state_dict"], strict=False)
        else:
            model.load_state_dict(checkpoint, strict=False)
        # Set the model to evaluation mode
        model.eval()
        logging.info("Deepfake detection model loaded successfully")
        return model
    except Exception as e:
        logging.error(f"Model loading error: {str(e)}")
        return None


# Initialize settings
settings = get_settings()