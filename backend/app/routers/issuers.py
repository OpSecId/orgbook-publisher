from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.web_requests import RegisterIdentifier
from config import settings
from app.plugins import AskarVerifier, AskarStorage, DidWebEndorser
from app.dependencies import identifier_available, did_document_exists, valid_did_registration

router = APIRouter()


@router.get("/issuers", summary="Request Identifier list.")
async def get_issuers(identifier: str):
    issuer_registrations = await AskarStorage().fetch('registration', 'issuers')
    return JSONResponse(
        status_code=200,
        content={
            "document": AskarVerifier().create_document_template(identifier),
            "options": AskarVerifier().create_proof_config(),
        },
    )


@router.post("/issuers", summary="Register Identifier.")
async def register_identifier(
    request_body: RegisterIdentifier, request: Request, did_document=Depends(valid_did_registration)
):
    identifier = vars(request_body)['identifier']
    did_doc = DidWebEndorser().request_did(identifier)
    issuer_registrations = await AskarStorage().fetch('registration', 'issuers')
    issuer_registrations['issuers'].append({
        'id': did_doc['id'],
        'name': vars(request_body)['name']
    })
    issuer_registrations = await AskarStorage().update('registration', 'issuers', issuer_registrations)
    return JSONResponse(status_code=201, content=did_doc)
