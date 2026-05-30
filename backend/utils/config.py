from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Brain Tumor Classification API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Model configuration
    MODEL_PATH: str = "../ml/checkpoints/best_model.onnx"
    CLASSES: List[str] = ["glioma", "meningioma", "notumor", "pituitary"]
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
