from fastapi import HTTPException
from config import settings
from app.plugins.agent import AgentController
from app.plugins import AskarWallet
from app.models import DidDocument, VerificationMethod, Service
import requests

class DidWebEndorser:
    def __init__(self):
        self.did = settings.TDW_ENDORSER_DID
        self.server = settings.TDW_SERVER_URL
        
    async def did_registration(self, namespace, identifier, url=None):
        did_request = self.request_did(
            namespace=namespace,
            identifier=identifier,
        )
        did_document = did_request['didDocument']
        did = did_document['id']
        multikey = await AskarWallet().create_key(f'{did}#key-01')
        # multikey = AgentController().create_key_pair(kid=f'{did}#key-01')
        did_document = DidDocument(
            id=did,
            authentication=[f'{did}#key-01'],
            assertionMethod=[f'{did}#key-01'],
            verificationMethod=[VerificationMethod(
                id=f'{did}#key-01',
                controller=did,
                publicKeyMultibase=multikey
            )]
        ).model_dump()
        # if url:
        #     did_doc['service'] = [{
        #         'id': did_doc['id']+'#ministry',
        #         'type': 'LinkedDomain',
        #         'serviceEndpoint': url,
        #     }]
        
        issuer_options = did_request['proofOptions'].copy()
        issuer_options['verificationMethod'] = f'{did}#key-01'
        signed_did_doc = await AskarWallet().add_proof(did_document, issuer_options)
        # signed_did_doc = AgentController().sign_document(did_doc, proof_options)
        endorser_options = did_request['proofOptions'].copy()
        endorsed_did_doc = await AskarWallet().add_proof(signed_did_doc, endorser_options)
        # endorsed_did_doc = AgentController().endorse_document(signed_did_doc, proof_options)
        
        did_registration = self.register_did(endorsed_did_doc)
        # print(did_registration)
        # return did_registration
        return endorsed_did_doc
        
    def request_did(self, namespace, identifier):
        r = requests.get(f'{self.server}?namespace={namespace}&identifier={identifier}')
        try:
            return r.json()
        except:
            raise HTTPException(status_code=r.status_code, detail="Couldn't request did.")
        
    def register_did(self, endorsed_did_doc):
        r = requests.post(f'{self.server}', json={
            'didDocument': endorsed_did_doc
        })
        try:
            return r.json()['didDocument']
        except:
            raise HTTPException(status_code=r.status_code, detail="Couldn't register did.")