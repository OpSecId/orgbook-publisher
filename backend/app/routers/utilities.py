from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models.web_schemas import RegisterIssuer
from config import settings
from app.plugins import AskarStorage
from app.models import DidDocument
import json

router = APIRouter()


@router.post("/utilities/oca-bundle-generator")
async def generate_oca_bundle(request_body: CredentialRegistration):
    pass
