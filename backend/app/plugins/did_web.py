from fastapi import HTTPException
from config import settings
from app.plugins import AgentController
import requests

class DidWebEndorser:
    def __init__(self):
        self.did = settings.ENDORSER_DID
        self.server = settings.DID_WEB_SERVER_URL
        
    def request_did(self, identifier):
        r = requests.get(f'{self.server}/{identifier}')
        try:
            return r.json()
        except:
            raise HTTPException(status_code=r.status_code, detail="Couldn't request did.")
        
    def register_did(self, identifier, endorsed_did_doc):
        r = requests.post(f'{self.server}/{identifier}', json={
            'didDocument': endorsed_did_doc
        })
        try:
            return r.json()
        except:
            raise HTTPException(status_code=r.status_code, detail="Couldn't register did.")
        
    def register_identifier(self, identifier):
        did_request = self.request_did(identifier)
        did_doc = did_request['document']
        
        verification_method = AgentController().register_did(did_doc['id'])
        did_doc['authentication'].append(verification_method['id'])
        did_doc['assertionMethod'].append(verification_method['id'])
        did_doc['verificationMethod'].append(verification_method)
        
        options = did_request['options']
        options['verificationMethod'] = verification_method['id']
        
        signed_did_doc = AgentController().sign_document(did_doc, options)
        endorsed_did_doc = AgentController().endorse_document(signed_did_doc, options)
        
        return self.request_did(identifier, endorsed_did_doc)