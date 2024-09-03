from fastapi import HTTPException
from config import settings
from datetime import datetime
import requests

class AgentController:
    def __init__(self):
        self.endpoint = settings.AGENT_ADMIN_URL
        self.headers = {'X-API-KEY': settings.AGENT_ADMIN_API_KEY}
        self.endorser = settings.ENDORSER_DID
        self.endorser_vm = settings.ENDORSER_VM
        
    def register_did(self, did, seed=None):
        r = requests.post(f'{self.server}/did/web', headers=self.headers, json={
            "id": f"{did}#key-01",
            "key_type": "ed25519",
            "seed": seed,
            "type": "MultiKey"
        })
        try:
            return r.json()["verification_method"]
        except:
            raise HTTPException(status_code=r.status_code, detail="Couldn't create did.")
        
    def issuer_proof_options(self):
        return {
            'type': 'DataIntegrityProof',
            'cryptosuite': 'eddsa-jcs-2022',
            'proofPurpose': 'assertionMethod',
            'created': datetime.now(),
        }
        
    def endorser_proof_options(self):
        return {
            'type': 'DataIntegrityProof',
            'cryptosuite': 'eddsa-jcs-2022',
            'verificationMethod': self.endorser_vm,
            'proofPurpose': 'authentication',
            'created': datetime.now(),
            'expires': datetime.now(),
        }
        
        
    def sign_document(self, document, options):
        r = requests.post(f'{self.server}/wallet/add-di-proof', headers=self.headers, json={
            'document': document,
            'options': options
        })
        signed_document = r.json()
        
    def endorse_document(self, document, options):
        options['verificationMethod'] = self.endorser_vm
        r = requests.post(f'{self.server}/wallet/add-di-proof', headers=self.headers, json={
            'document': document,
            'options': options
        })
        endorsed_document = r.json()