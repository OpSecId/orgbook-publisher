from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.registrations import IssuerRegistration, CredentialRegistration
from config import settings
from app.plugins import AskarStorage, BitstringStatusList, PublisherRegistrar, Soup
from app.security import check_api_key_header

router = APIRouter(prefix='/registrations', tags=["Registrations"])


@router.post("/issuers")
async def register_issuer(request_body: IssuerRegistration, authorized = Depends(check_api_key_header)):
    registration = vars(request_body)
    did_document = PublisherRegistrar().register_issuer(
        registration["name"], 
        registration["scope"], 
        registration["url"], 
        registration["description"],
        registration["multikey"],
    )

    await AskarStorage().store('issuer', did_document['id'], did_document)
    issuer = {
        'id': did_document['id'],
        'name': registration["name"],
        'scope': registration["scope"],
    }
    return JSONResponse(status_code=201, content=issuer)


@router.delete("/issuers/{did}")
async def delete_issuer(did: str, authorized = Depends(check_api_key_header)):
        
    await AskarStorage().remove('issuer', did)
    return JSONResponse(status_code=200, content={})


@router.post("/credentials")
async def register_credential_type(request_body: CredentialRegistration, authorized = Depends(check_api_key_header)):
    credential_registration = request_body.model_dump()

    # Create a new status list for this type of credential
    # status_list = await BitstringStatusList().create(credential_registration)
    # credential_registration["statusList"] = [status_list]
    # await AskarStorage().replace(
    #     "credentialRegistration",
    #     credential_registration["type"],
    #     credential_registration,
    # )
    # return JSONResponse(status_code=201, content=credential_registration)
    credential_template = await PublisherRegistrar().register_credential(credential_registration)
    # await AskarStorage().replace(
    #     "credentialTemplate",
    #     credential_registration["type"],
    #     credential_template,
    # )
    return JSONResponse(status_code=201, content=credential_template)
