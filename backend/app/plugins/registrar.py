from config import settings
from fastapi import HTTPException
import requests
from app.models import DidDocument, VerificationMethod, Service
from app.plugins.traction import TractionController
from app.utilities import multikey_to_jwk


class PublisherRegistrar:
    
    def __init__(self):
        self.tdw_server = settings.TDW_SERVER_URL
        self.endorser_multikey = settings.TDW_ENDORSER_MULTIKEY
    
    def register_issuer(self, name, scope, url, description):
        namespace = scope.replace(" ", "-").lower()
        identifier = name.replace(" ", "-").lower()
        r = requests.get(f'{self.tdw_server}?namespace={namespace}&identifier={identifier}')
        try:
            did = r.json()['didDocument']['id']
        except:
            raise HTTPException(status_code=r.status_code, detail=r.json())
            
        
        multikey_kid = f'{did}#multikey-01'
        jwk_kid = f'{did}#jwk-01'
        
        traction = TractionController()
        # traction.authorize()
        multikey = traction.create_did_key()
        # traction.bind_key(multikey, multikey_kid)
    
        verification_method_multikey = VerificationMethod(
            id=multikey_kid,
            type='Multikey',
            controller=did,
            publicKeyMultibase=multikey
        )
    
        verification_method_jwk = VerificationMethod(
            id=jwk_kid,
            type='JsonWebKey',
            controller=did,
            publicKeyJwk=multikey_to_jwk(multikey)
        )
    
        service = Service(
            id=f'{did}#bcgov-website',
            type='LinkedDomains',
            serviceEndpoint=url,
        ) if url else None

        did_document = DidDocument(
            id=did, 
            name=name, 
            description=description,
            authentication=[verification_method_multikey.id],
            assertionMethod=[verification_method_multikey.id],
            verificationMethod=[
                verification_method_multikey,
                verification_method_jwk
            ],
            service=[service] if service else None
        ).model_dump()
        
        client_proof_options = r.json()['proofOptions'].copy()
        client_proof_options['verificationMethod'] = f'did:key:{multikey}#{multikey}'
        signed_did_document = traction.add_di_proof(did_document, client_proof_options)
        
        endorser_proof_options = r.json()['proofOptions'].copy()
        endorser_proof_options['verificationMethod'] = f'did:key:{self.endorser_multikey}#{self.endorser_multikey}'
        endorsed_did_document = traction.add_di_proof(signed_did_document, endorser_proof_options)
        
        r = requests.post(f'{self.tdw_server}/{namespace}/{identifier}', json={
            'didDocument': endorsed_did_document
        })
        try:
            return r.json()['didDocument']
        except:
            raise HTTPException(status_code=r.status_code, detail=r.json())

    def register_credential(self):
        pass
    
    def publish_credential(self, credential_data):
        credential_registration = {}
        credential = {
            'credentialSubject': {}
        }
        if 'untpType' in credential_registration:
            if credential_registration['untpType'] == 'DigitalConformityCredential':
                type = ['ConformityAttestation']
                attestationType = "Certification"
                assessmentLevel = "GovtApproval"
                scope = {
                    "id": "https://bcgov.github.io/digital-trust-toolkit/docs/governance/pilots/bc-petroleum-and-natural-gas-title/governance",
                    "name": "B.C. Petroleum & Natural Gas Title - DRAFT"
                }
                issuedToParty = {
                    "id": "https://orgbook.gov.bc.ca/entity/A0131571",
                    "idScheme": {
                        "id": "https://www.bcregistry.gov.bc.ca/",
                        "name": "BC Registry",
                        "type": "IdentifierScheme"
                    },
                    "name": "PACIFIC CANBRIAM ENERGY LIMITED",
                    "registeredId": credential_data['entityId'],
                    "type": [
                        "Entity",
                    ]
                }
                assessment = {
                    "type": ["ConformityAssessment"],
                    "conformityTopic": "Governance.Compliance",
                    "compliance": True,
                    "referenceRegulation": {
                        "administeredBy": {
                                "id": "https://www2.gov.bc.ca/gov/content/home",
                                "idScheme": {
                                    "id": "https://www2.gov.bc.ca/gov/content/home",
                                    "name": "BC-GOV",
                                    "type": "IdentifierScheme"
                                },
                            "name": "Government of British Columbia",
                            "registeredId": "BC-GOV",
                            "type": [
                                "Entity"
                            ]
                        },
                        "effectiveDate": act_soup['date'],
                        "id": credential_registration['legalAct'],
                        "jurisdictionCountry": "CA",
                        "name": act_soup['title'],
                        "type": [
                            "Regulation"
                        ]
                    }
                }
                assessedFacility = []
                assessedProduct = []
                facility = {
                    "type": ["Facility"]
                }
                product = {
                    "type": ["Product"]
                }
                
            act_soup = {}