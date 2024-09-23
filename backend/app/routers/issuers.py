from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.web_requests import RegisterIssuer
from config import settings
from app.plugins import AskarStorage, DidWebEndorser

router = APIRouter()

@router.get("/issuers", summary="Request issuers list.")
async def get_issuers():
    issuer_registrations = await AskarStorage().fetch('registration', 'issuers')
    return JSONResponse(
        status_code=200,
        content=issuer_registrations,
    )

@router.post("/issuers", summary="Register issuer.")
async def register_issuer(
    request_body: RegisterIssuer
):
    # did_doc = DidWebEndorser().did_registration(
    #     namespace=vars(request_body)['namespace'] if vars(request_body)['namespace'] else 'issuer', 
    #     identifier=vars(request_body)['identifier']
    # )
    identifier = vars(request_body)['identifier']
    namespace = vars(request_body)['namespace']
    did = f'did:web:{settings.DOMAIN}:{identifier}:{namespace}'
    did = f'did:web:digitaltrust.traceability.site:petroleum-and-natural-gas-act:director-of-petroleum-lands'
    await AskarStorage().add_issuer(
        did=did,
        name=vars(request_body)['name'],
        description=vars(request_body)['description'],
    )
    return JSONResponse(status_code=201, content={'status': 'ok'})
