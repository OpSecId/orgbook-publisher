from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.registrations import IssuerRegistration, CredentialRegistration
from config import settings
from app.plugins import (
    AskarStorage,
    BitstringStatusList,
    PublisherRegistrar,
    Soup,
    OrgbookPublisher,
)
from app.security import check_api_key_header

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.post("/issuers")
async def register_issuer(
    request_body: IssuerRegistration, authorized=Depends(check_api_key_header)
):
    registration = vars(request_body)
    did_document = PublisherRegistrar().register_issuer(
        registration["name"],
        registration["scope"],
        registration["url"],
        registration["description"],
        registration["multikey"],
    )
    await AskarStorage().store("issuer", did_document["id"], did_document)
    authorized_key = did_document["verificationMethod"][0]["publicKeyMultibase"]
    await AskarStorage().store("authorizedKey", did_document["id"], authorized_key)
    issuer = {
        "id": did_document["id"],
        "name": registration["name"],
        "scope": registration["scope"],
    }
    return JSONResponse(status_code=201, content=issuer)


@router.post("/credentials")
async def register_credential_type(
    request_body: CredentialRegistration, authorized=Depends(check_api_key_header)
):
    credential_registration = request_body.model_dump()

    # Create a new status list for this type of credential
    status_list_id = await BitstringStatusList().create(credential_registration)
    credential_registration["statusList"] = [status_list_id]
    await AskarStorage().replace(
        "credentialRegistration",
        credential_registration["type"],
        credential_registration,
    )

    credential_template = await PublisherRegistrar().template_credential(
        credential_registration
    )
    await AskarStorage().replace(
        "credentialTemplate",
        credential_registration["type"],
        credential_template,
    )

    await OrgbookPublisher().create_credential_type(credential_registration, issuer['verificationMethod'][0]['id'])
    return JSONResponse(status_code=201, content=credential_registration)
