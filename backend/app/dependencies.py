from fastapi import HTTPException
from config import settings
from app.models.web_requests import RegisterDID
from app.plugins import AskarVerifier, AskarStorage