from ..services.inference import model_service

def get_model_service():
    """Dependency injection for the model service."""
    return model_service
