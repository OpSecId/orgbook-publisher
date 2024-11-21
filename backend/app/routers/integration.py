from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from app.models.integration import (
    IssuerRegistration,
    CredentialRegistration,
    Publication,
    RequestSecret,
    RequestToken,
)
from app.plugins import AskarStorage, BitstringStatusList
from app.plugins.integration import IntegrationModule
from app.auth.bearer import JWTBearer
from app.security import check_api_key_header
import uuid
import random
from config import settings

router = APIRouter(prefix="/integration", tags=["Integration"])


@router.post("/register-issuer", dependencies=[Depends(check_api_key_header)])
async def issuer_registration_integration(request_body: IssuerRegistration):
    did_document = await IntegrationModule().create_did_document(
        registration=vars(request_body)
    )
    return JSONResponse(status_code=201, content=did_document)


# @router.post("/create-delegated-issuer-credential")
# async def create_qrcode(url: str):
#     did_document = ''
#     pickup_qr_code = IntegrationModule().create_delegated_issuer_credential(
#         did_document=did_document
#     )
#     return StreamingResponse(pickup_qr_code, media_type="image/jpeg")


@router.post("/secret", dependencies=[Depends(check_api_key_header)])
async def get_integration_secret(request_body: RequestSecret):
    client_secret = await IntegrationModule().create_client_secret(
        client_id=vars(request_body)["client_id"]
    )
    return JSONResponse(status_code=200, content={"client_secret": client_secret})


@router.post("/token")
async def get_integration_token(request_body: RequestToken):
    access_token = await IntegrationModule().request_token(
        client_id=vars(request_body)["client_id"],
        client_secret=vars(request_body)["client_secret"],
    )
    return JSONResponse(status_code=200, content={"access_token": access_token})


@router.post("/register-credential", dependencies=[Depends(check_api_key_header)])
async def credential_registration_integration(request_body: CredentialRegistration):
    credential_registration = request_body.model_dump()

    # Register credential type and create template
    credential_template = await IntegrationModule().create_credential_type(
        credential_registration=credential_registration
    )

    return JSONResponse(status_code=200, content=credential_template)


@router.post("/publish-credential", dependencies=[Depends(JWTBearer())])
async def publish_credential_integration(request_body: Publication):
    credential = await IntegrationModule().publish_credential(
        credential=request_body.model_dump()["credential"],
        options=request_body.model_dump()["options"],
    )

    return JSONResponse(status_code=201, content=credential)
    return JSONResponse(status_code=201, content={"credentialId": credential["id"]})
