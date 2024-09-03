from fastapi import APIRouter, Depends, HTTPException, Request
from config import settings
from app.models import Credential, DigitalConformityCredential
from app.utilities import freeze_ressource_digest
from app.plugins import AgentController, AskarStorage
import requests
import uuid

class OrgbookPublisher:
    
    def __init__(self):
        self.api = settings.ORGBOOK_API_URL
        self.orgbook = settings.ORGBOOK_URL
        self.microservice = settings.ORGBOOK_MICROSERVICE_URL
        
    def fetch_buisness_info(self, identifier):
        pass
        
    async def create_credential_type(self, credential_type):
        credential_type['context'] = freeze_ressource_digest(credential_type['context'])
        credential_type['ocaBundle'] = freeze_ressource_digest(credential_type['ocaBundle'])
        credential_type['jsonSchema'] = freeze_ressource_digest(credential_type['jsonSchema'])
        credential_type['governance'] = freeze_ressource_digest(credential_type['governance'])
        credential_type['vocabulary'] = freeze_ressource_digest(credential_type['vocabulary'])

        await AskarStorage().store('credentialTypes', credential_type['type'], credential_type)
        
        secured_credential_type = AgentController().sign_document(credential_type)
        
        r = requests.post(f'{self.microservice}/credential-types', json={'securedDocument': secured_credential_type})
        
    async def publish_credential(self, entity_id, credential, credential_type):
        credential_type = await AskarStorage().fetch('credentialType', credential_type)
        credential = self._format_credential(entity_id, credential, credential_type)
        secured_document = self._secure_credential(credential, credential_type['verificationMethod'])
        
        r = requests.post(f'{self.microservice}/credentials', json={
            'securedDocument': secured_document,
            'options': {
                'credentialType': credential_type['type'],
                'credentialVersion': credential_type['version'],
            }
        })
        try:
            return r.json()
        except:
            return {}
        
    async def _format_credential(self, entity_id, credential, credential_type):
        credential = Credential(
            id=f'{self.microservice}/entity/{entity_id}/credentials/{str(uuid.uuid4())}'
        )
        credential.type.append(credential_type['type'])
        credential.name = credential_type['name']
        credential.description = credential_type['description']
        credential.issuer = self._find_issuer(self, credential_type['verificationMethod'])
        credential.credentialSchema.append({
                'type': 'JsonSchema',
                'id': credential_type['jsonSchema']['url'],
                'digest': credential_type['jsonSchema']['digest'],
            })
        # credential.credentialStatus.append()
        credential.renderMethod.append({
                'type': 'OverlayCaptureBundle',
                'id': credential_type['ocaBundle']['url'],
                'digest': credential_type['ocaBundle']['digest'],
        })
        credential.termsOfUse.append({
                'type': 'GovernanceFramework',
                'id': credential_type['governance']['url'],
                'digest': credential_type['governance']['digest'],
            })
        
        # UNTP
        if 'DigitalConformityCredential' in credential_type['extraTypes']:
            credential.context.append('')
            credential.type.append('DigitalConformityCredential')
            credential.credentialSubject.issuedTo = self._find_entity(self, entity_id)

        # BC Gov
        credential.context.append(credential_type['context']['url'])
        if credential_type['type'] == 'PetroleumAndNaturalGasTitle':
            pass
        
        return credential
        
    async def _secure_credential(self, credential, verification_method):
        
        options = AgentController().issuer_proof_options()
        options['verificationMethod'] = verification_method
        vc = AgentController().sign_document(credential, options)
        
        presentation = {
            '@context': [],
            'type': ['VerifiablePresentation'],
            'credentialSubject': [vc]
        }
        options = AgentController().endorser_proof_options()
        vp = AgentController().sign_document(presentation, options)
        return vp
        
    async def _find_entity(self, entity_id):
        entity = {
            'id': '',
            'name': '',
        }
        return entity
        
    async def _find_issuer(self, verification_method):
        issuer = {
            'id': '',
            'name': '',
        }
        return issuer