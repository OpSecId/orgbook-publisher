from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.web_schemas import RegisterCredential, IssueCredential
from config import settings
from app.plugins.untp import UNTP_CONTEXTS
from app.plugins import AskarVerifier, AskarStorage, AskarWallet, DidWebEndorser, OrgbookPublisher
from app.utilities import freeze_ressource_digest
import uuid
from datetime import datetime
import json

import base64

router = APIRouter()


@router.post("/credentials/register")
async def register_credential(request_body: RegisterCredential):
    credential_registration = request_body.model_dump()['credentialRegistration']
    # TODO remove me
    credential_registration['issuer'] = settings.ISSUERS[0]['id']
    try:
        await AskarStorage().store('credentialRegistration', credential_registration['type'], credential_registration)
    except:
        await AskarStorage().update('credentialRegistration', credential_registration['type'], credential_registration)
    credential_type = await OrgbookPublisher().create_credential_type(credential_registration)
    return JSONResponse(
        status_code=201,
        content=credential_type,
    )


@router.post("/credentials/issue")
async def issue_credential(request_body: IssueCredential):
    credential = request_body.model_dump()['credential']
    
    options = request_body.model_dump()['options']
    
    try:
        credential_registration = await AskarStorage().fetch('credentialRegistration', options['credentialType'])
    except:
        raise HTTPException(status_code=404, detail="Unknown credential type.")
    
    
    # W3C type and context
    contexts = ['https://www.w3.org/ns/credentials/v2']
    types = ['VerifiableCredential']
    
    # UNTP type and context
    if 'untpType' in credential_registration:
        contexts.append(UNTP_CONTEXTS[credential_registration['untpType']])
        types.append(credential_registration['untpType'])
        
    # BCGov type and context
    contexts.append(credential_registration['ressources']['context'])
    types.append(credential_registration['type'])
    
    credential_id = str(uuid.uuid4())
    issuer = next((issuer for issuer in settings.ISSUERS if issuer['id'] == credential_registration['issuer']), None)
    
    credential = {
        '@context': contexts,
        'type': types,
        'id': f'https://{settings.DOMAIN}/credentials/{credential_id}',
        'issuer': issuer,
        'name': credential_registration['name'],
        'description': credential_registration['description']
        } | credential
    
    # TODO, find a better way to get verification method
    verification_method = credential_registration['issuer']+'#multikey-01'
    
    proof_options = {
        'type': 'DataIntegrityProof',
        'cryptosuite': 'eddsa-jcs-2022',
        'proofPurpose': 'assertionMethod',
        'verificationMethod': verification_method,
        'created': str(datetime.now().isoformat('T', 'seconds'))
    }
    
    vc = await AskarWallet().add_proof(credential, proof_options)
    await AskarStorage().store('credential', credential_id, vc)
    
    return JSONResponse(
        status_code=201,
        content=vc
    )

@router.get("/credentials/{credential_id}")
async def get_credential(credential_id: str, envelope: bool = False):
    headers = {"Content-Type": "application/ld+json"}
    vc = await AskarStorage().fetch('credential', credential_id)
    if envelope:
        vc = await AskarWallet().sign_vc_jose(vc)
    return JSONResponse(
        status_code=200,
        content=vc,
        headers=headers
    )


@router.post("/credentials/status")
async def update_credential_status(request_body: IssueCredential):
    pass


@router.get("/credentials/status/{status_credential_id}")
async def get_status_list_credential(status_credential_id: str):
    pass




