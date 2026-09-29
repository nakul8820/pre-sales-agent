from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Use in-memory if Redis url is missing, otherwise attempt to use redis
def create_limiter(redis_url: str = None) -> Limiter:
    if redis_url:
        try:
            # We must use sync redis for slowapi storage 
            # (or use a compatible async library, but slowapi natively supports sync redis via limits package)
            limiter = Limiter(
                key_func=get_remote_address,
                storage_uri=redis_url,
                default_limits=["100/minute"]
            )
            return limiter
        except Exception as e:
            logger.error(f"Failed to configure Redis for SlowAPI, falling back to memory: {e}")
            
    # Fallback to in-memory
    return Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        {"error": "RateLimitExceeded", "message": f"Rate limit exceeded: {exc.detail}"},
        status_code=429
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response

def setup_rate_limiting(app: FastAPI, redis_url: str = None):
    limiter = create_limiter(redis_url)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
