from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models.web_schemas import RegisterIssuer
from config import settings
from app.plugins import AskarStorage
from app.models import DidDocument
import json

router = APIRouter()

@router.get("/contexts/{filename}/v1")
async def get_context_file(filename: str):
    try:
        headers = {"Content-Type": "application/ld+json"}
        with open(f'app/related_resources/contexts/{filename}.jsonld', 'r') as f:
            context = json.loads(f.read())
        return JSONResponse(status_code=200, content=context, headers=headers)
    except:
        raise HTTPException(status_code=404, detail="Ressource not found.")