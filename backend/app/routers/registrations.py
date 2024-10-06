from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.registrations import IssuerRegistration, CredentialRegistration
from config import settings
from app.plugins import AskarStorage, BitstringStatusList, PublisherRegistrar, Soup
from app.security import check_api_key_header

router = APIRouter(prefix='/registrar')


@router.post("/issuers")
async def register_issuer(request_body: IssuerRegistration, authorized = Depends(check_api_key_header)):
    namespace = vars(request_body)["scope"].replace(" ", "-").lower()
    identifier = vars(request_body)["name"].replace(" ", "-").lower()
    issuer = {
        'id': f'did:web:{settings.TDW_SERVER_URL.split("//")[-1]}:{namespace}:{identifier}',
        'name': vars(request_body)["name"],
        'description': vars(request_body)["description"]
    }
    await AskarStorage().store('didRegistration', issuer['id'], issuer)
    return JSONResponse(status_code=201, content=issuer)

    did_document = PublisherRegistrar().register_issuer(
        vars(request_body)["name"], 
        vars(request_body)["scope"], 
        vars(request_body)["url"], 
        vars(request_body)["description"]
    )
        
    await AskarStorage().store('didRegistration', did_document['id'], did_document)
    return JSONResponse(status_code=201, content=did_document)

# @router.post("/issuers/{did}")
# async def approve_pending_issuer_registration(did: str):
#     did_document = await AskarStorage().fetch('didRegistration', did)
#     await AskarStorage().store('didDocument', did, did_document)
#     # await AskarStorage().remove('didRegistration', did)
#     return JSONResponse(
#         status_code=200,
#         content=did_document,
#     )


@router.delete("/issuers/{did}")
async def register_issuer(did: str, authorized = Depends(check_api_key_header)):
        
    await AskarStorage().remove('didRegistration', did)
    return JSONResponse(status_code=200, content={})


@router.post("/credentials")
async def register_credential_type(request_body: CredentialRegistration, authorized = Depends(check_api_key_header)):
    credential_registration = request_body.model_dump()
    
    untp_type = credential_registration.get('untpType')
    if untp_type == 'DigitalConformityCredential':
        if not credential_registration['relatedResources'].get('governance') \
            or not credential_registration['relatedResources'].get('legalAct'):
                pass
        governance = {
            'id': credential_registration['relatedResources'].get('governance').lstrip('/'),
            'name': credential_registration['relatedResources'].get('governance').lstrip('/').split('/')[-1].replace('-', ' ').title()
        }
        legal_act = Soup(
            credential_registration['relatedResources'].get('legalAct')
        ).legal_act_info()

    # Create a new status list for this type of credential
    # status_list = await BitstringStatusList().create(credential_registration)
    # credential_registration["statusList"] = [status_list]

    await AskarStorage().replace(
        "credentialRegistration",
        credential_registration["type"],
        credential_registration,
    )
        
    return JSONResponse(status_code=201, content=credential_registration)
