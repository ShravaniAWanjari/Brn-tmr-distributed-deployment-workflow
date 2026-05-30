import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class StructlogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            client_ip=request.client.host if request.client else None
        )
        
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            
            logger.info(
                "Request processed",
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2)
            )
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.exception(
                "Request failed",
                process_time_ms=round(process_time * 1000, 2),
                error=str(e)
            )
            raise e
