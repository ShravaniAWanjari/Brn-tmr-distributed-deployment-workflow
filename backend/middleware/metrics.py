import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from metrics.prometheus import REQUEST_COUNT, REQUEST_LATENCY

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            process_time = time.perf_counter() - start_time
            REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)
            REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, http_status=response.status_code).inc()
            
            return response
            
        except Exception as e:
            # Note: We don't record a 500 status here if the exception isn't caught yet by FastAPI,
            # but standard exception handlers should convert this properly.
            raise e
