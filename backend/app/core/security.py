"""Security and rate-limiting helper utilities."""
from typing import Optional
from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_api_token(x_api_token: Optional[str] = Header(None)) -> bool:
    """Optional middleware/dependency to verify incoming internal API tokens."""
    if settings.ENVIRONMENT == "production":
        if not x_api_token or x_api_token != settings.SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API authorization token.",
            )
    return True
