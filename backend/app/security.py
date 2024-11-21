from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader
from starlette import status
from config import settings
from app.plugins import AskarStorage
import secrets
import hashlib

X_API_KEY = APIKeyHeader(name="X-API-Key")
ACCESS_TOKEN = HTTPBearer()


def hash(value: str):
    return hashlib.sha256(value.encode()).hexdigest()


async def update_client_secret(client_id: str):
    client_secret = secrets.token_urlsafe(32)
    await AskarStorage().replace("clientHash", client_id, hash(client_secret))
    return client_secret


async def verify_client_secret(client_id: str, client_secret: str):
    client_hash = await AskarStorage().fetch("clientHash", client_id)
    return True if client_hash == hash(client_secret) else False


def check_api_key_header(x_api_key: str = Depends(X_API_KEY)):
    """Check api key"""

    if x_api_key == settings.TRACTION_API_KEY:
        return True
    raise HTTPException(
        status_code=401,
        detail="Invalid API Key",
    )


def check_access_token_header(access_token: str = Depends(ACCESS_TOKEN)):
    """Check access token"""
    print(access_token)
    return True

    # if x_api_key == settings.TRACTION_API_KEY:
    #     return True
    # raise HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Invalid API Key",
    # )
