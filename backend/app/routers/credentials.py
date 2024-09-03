from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.web_requests import CredentialType, PublishCredential
from config import settings
from app.plugins import AskarVerifier, AskarStorage, DidWebEndorser, OrgbookPublisher
from app.utilities import freeze_ressource_digest

router = APIRouter()


@router.post("/credential-types", summary="Create new credential type.")
async def create_credential_type(request_body: CredentialType):
    credential_type = await OrgbookPublisher().create_credential_type(vars(request_body))
    return JSONResponse(
        status_code=200,
        content=credential_type,
    )


@router.post("/credentials/publish", summary="Publish Credential.")
async def publish_credential(request_body: PublishCredential):
    response = await OrgbookPublisher().publish_credential(
        entity_id=vars(request_body)['registrationId'],
        credential=vars(request_body)['credential'],
        credential_type= vars(request_body)['credentialType']
    )
    return JSONResponse(
        status_code=200,
        content=response,
    )


