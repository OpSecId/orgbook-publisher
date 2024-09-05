from fastapi import HTTPException
from config import settings
from app.plugins.agent import AgentController
import requests

class DidWebEndorser:
    def __init__(self):
        self.did = settings.ENDORSER_DID
        self.server = settings.DID_WEB_SERVER_URL
        
    def request_did(self, namespace, identifier):
        r = requests.get(f'{self.server}/{namespace}/{identifier}')
        try:
            return r.json()
        except:
            raise HTTPException(status_code=r.status_code, detail="Couldn't request did.")
        
    def register_did(self, namespace, identifier, endorsed_did_doc):
        r = requests.post(f'{self.server}/{namespace}/{identifier}', json={
            'didDocument': endorsed_did_doc
        })
        try:
            return r.json()['didDocument']
        except:
            raise HTTPException(status_code=r.status_code, detail="Couldn't register did.")
        
    def did_registration(self, namespace, identifier):
        did_request = self.request_did(namespace, identifier)
        did_doc = did_request['document']
        
        verification_method = AgentController().register_did(did_doc['id'])
        did_doc['@context'].append('https://w3id.org/security/multikey/v1')
        did_doc['authentication'] = [verification_method['id']]
        did_doc['assertionMethod'] = [verification_method['id']]
        did_doc['verificationMethod'] = [verification_method]
        
        proof_options = did_request['options']
        proof_options['verificationMethod'] = verification_method['id']
        
        signed_did_doc = AgentController().sign_document(did_doc, proof_options)
        endorsed_did_doc = AgentController().endorse_document(signed_did_doc, proof_options)
        
        did_registration = self.register_did(namespace, identifier, endorsed_did_doc)
        return did_registration