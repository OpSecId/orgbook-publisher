from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.web_requests import RegisterCredential, PublishCredential
from config import settings
from app.plugins import AskarVerifier, AskarStorage, DidWebEndorser, OrgbookPublisher
from app.utilities import freeze_ressource_digest

router = APIRouter()


@router.post("/credentials/register", summary="Register new credential.")
async def register_credential(request_body: RegisterCredential):
    credential_registration = request_body.model_dump()['credentialRegistration']
    try:
        await AskarStorage().store('credentialRegistration', credential_registration['type'], credential_registration)
    except:
        await AskarStorage().update('credentialRegistration', credential_registration['type'], credential_registration)
    credential_type = await OrgbookPublisher().create_credential_type(credential_registration)
    return JSONResponse(
        status_code=201,
        content=credential_type,
    )


@router.post("/credentials/publish", summary="Publish Credential.")
async def publish_credential(request_body: PublishCredential):
    credential_registration = await AskarStorage().fetch('credentialRegistration', request_body.model_dump()['credentialType'])
    published_credential = await OrgbookPublisher().publish_credential(
        claims=request_body.model_dump()['credentialClaims'],
        credential_registration=credential_registration
    )
    return JSONResponse(
        status_code=201,
        content=published_credential,
    )


