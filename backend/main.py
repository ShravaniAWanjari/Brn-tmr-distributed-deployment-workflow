from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
import uvicorn

from utils.config import settings
from middleware.logging import StructlogMiddleware
from middleware.metrics import PrometheusMiddleware
from api.router import router
from services.inference import model_service

logger = structlog.get_logger()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middlewares (Order matters: outermost first)
    app.add_middleware(StructlogMiddleware)
    app.add_middleware(PrometheusMiddleware)

    # Include API router
    app.include_router(router)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Application starting up...")
        # Initialize the model at startup so the first request isn't slow
        try:
            model_service.load_model()
        except Exception as e:
            logger.error("Error initializing model service during startup", error=str(e))
            # In a strict production environment, we might sys.exit(1) here if the model is mandatory
            
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
