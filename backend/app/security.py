from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from config import settings

X_API_KEY = APIKeyHeader(name='X-API-Key')

def check_api_key_header(x_api_key: str = Depends(X_API_KEY)):
    """ takes the X-API-Key header and converts it into the matching user object from the database """

    if x_api_key == settings.TRACTION_API_KEY:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )