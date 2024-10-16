from fastapi import APIRouter, Depends, HTTPException, Request
from config import settings
from app.models import Credential
from app.utilities import freeze_ressource_digest
from app.plugins import AskarStorage, AskarWallet
from app.plugins.untp import DigitalConformityCredential
from app.plugins.traction import TractionController

# from .ips import IPSView
import requests
import uuid
from datetime import datetime


class OrgbookPublisher:
    def __init__(self):
        self.api = settings.ORGBOOK_API_URL
        self.orgbook = settings.ORGBOOK_URL
        self.vc_service = settings.ORGBOOK_VC_SERVICE

    def fetch_buisness_info(self, identifier):
        pass

    async def create_credential_type(
        self, credential_registration, verification_method
    ):
        credential_type = {
            "format": "vc_di",
            "type": credential_registration["type"],
            "issuer": credential_registration["issuer"],
            "version": credential_registration["version"],
            "verificationMethods": [verification_method],
            "ocaBundle": {},
            "topic": {
                "type": "registration.registries.ca",
                "sourceId": {"path": credential_registration["mappings"]["entityId"]},
            },
            "mappings": [
                {"path": "$.validFrom", "type": "effective_date", "name": "validFrom"},
                {"path": "$.validUntil", "type": "expiry_date", "name": "validUntil"},
            ],
        }
        proof_options = {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-jcs-2022",
            "proofPurpose": "authentication",
            # 'proofPurpose': 'assertionMethod',
            "verificationMethod": verification_method,
        }
        signed_vc_type = await AskarWallet().add_proof(credential_type, proof_options)
        options = {"issuerId": credential_registration["issuer"]}
        # request_body = {'securedDocument': signed_vc_type, 'options': options}
        return signed_vc_type

        r = requests.post(f"{self.vc_service}/credential-types", json=request_body)
        try:
            return r.json()
        except:
            raise HTTPException(
                status_code=400, detail="Couldn't register credential type."
            )

    async def publish_credential(self, claims, credential_registration):
        credential = await self._format_credential(claims, credential_registration)
        vp = await self._secure_credential(
            credential, credential_registration["verificationMethod"]
        )
        credential["proof"] = [
            {
                "type": "DataIntegrityProof",
                "cryptosuite": "eddsa-jcs-2022",
                "proofPurpose": "assertionMethod",
                "verificationMethod": credential_registration["verificationMethod"],
                "proofValue": "",
            }
        ]
        payload = {
            "securedDocument": credential,
            "options": {
                "format": "vc_di",
                "type": credential_registration["type"],
                "credentialId": credential["id"],
                "credentialType": credential_registration["type"],
                "version": credential_registration["version"],
            },
        }

        r = requests.post(f"{self.vc_service}/credentials", json=payload)
        try:
            return r.json()
        except:
            raise HTTPException(
                status_code=400, detail="Couldn't register credential type."
            )

        # r = requests.post(f'{self.microservice}/credentials', json={
        #     'verifiablePresentation': secured_document,
        #     'options': {
        #         'issuerId': credential_registration['verificationMethod'].split('#')[-1],
        #         'credentialId': credential['id'],
        #         'credentialType': credential_registration['type'],
        #         'credentialVersion': credential_registration['version'],
        #     }
        # })
        # try:
        #     return r.json()
        # except:
        #     return {}

    async def _format_credential(self, claims, credential_registration):
        entity = await self._find_entity(claims["registrationNumber"])
        issuer = await self._find_issuer(
            credential_registration["verificationMethod"].split("#")[0]
        )
        credential = Credential(
            id=f"{self.vc_service}/credentials/{str(uuid.uuid4())}",
            issuer=issuer,
            name=credential_registration["name"],
            description=credential_registration["description"],
        ).model_dump()
        credential["validFrom"] = str(datetime.now().isoformat("T", "seconds"))
        credential["validUntil"] = str(datetime.now().isoformat("T", "seconds"))
        credential["credentialSubject"] = {}
        # credential['credentialSchema'] = {
        #         'type': 'JsonSchema',
        #         'id': credential_registration['ressources']['jsonSchema']
        #     }
        # credential['renderMethod'] = {
        #         'type': 'OverlayCaptureBundle',
        #         'id': credential_registration['ressources']['ocaBundle']
        # }
        # credential['termsOfUse'] = {
        #         'type': 'GovernanceFramework',
        #         'id': credential_registration['ressources']['governance']
        #     }
        # credential['credentialStatus'] = {
        #     'type': 'BitstringStatusListEntry',
        #     'statusPurpose': 'revocation',
        #     'statusListIndex': '123',
        #     'statusListCredential': 'https://',
        # }

        # UNTP
        if "DigitalConformityCredential" in credential_registration["extraTypes"]:
            credential = DigitalConformityCredential().vc_to_dcc(
                credential, credential_registration, entity
            )

        # BC Gov
        credential["@context"].append(credential_registration["ressources"]["context"])
        credential["type"].append(credential_registration["type"])

        if credential_registration["type"] == "BCPetroleum&NaturalGasTitle":
            # IPSView().get_holders(entity, claims['titleNumber'])
            # await IPSView().get_holders()
            pass
            # try:
            #     title = IPSView().get_title_info(entity, claims['titleNumber'])
            # except:
            #     pass
            # credential['credentialSubject']['type'].append()
            # credential['credentialSubject']['titleNumber'] = claims['titleNumber']
            # credential['credentialSubject']['originType'] = claims['titleNumber']
            # credential['credentialSubject']['originNumber'] = claims['titleNumber']
            # credential['credentialSubject']['issuedToParty']['type'].append('TitleHolder')
            # credential['credentialSubject']['issuedToParty']['interest'] = 100.000
            # assessment = {
            #     'type': ['ConformityAssessment', 'Petroleum&NaturalGasTitle'],
            #     'assessedFacilities': [],
            #     'assessedProducts': [],
            # }
            # credential = DigitalConformityCredential().add_assessment(credential, assessment)

        return credential

    async def _secure_credential(self, credential, verification_method):
        # options = AgentController().issuer_proof_options(verification_method)
        # vc = AgentController().sign_document(credential, options)
        credential["proof"] = [
            {
                "type": "DataIntegrityProof",
                "cryptosuite": "eddsa-jcs-2022",
                "proofPurpose": "assertionMethod",
                "verificationMethod": verification_method,
                "proofValue": "",
            }
        ]
        vc = credential

        presentation = {}
        # vp = AgentController().sign_document(presentation, options)
        presentation["proof"] = [
            {
                "type": "DataIntegrityProof",
                "cryptosuite": "eddsa-jcs-2022",
                "proofPurpose": "authentication",
                "verificationMethod": verification_method,
                "proofValue": "",
            }
        ]
        vp = presentation

        # options = AgentController().endorser_proof_options()
        # endorsed_vp = AgentController().sign_document(vp, options)
        # print(vp)
        return vp

    async def _find_entity(self, entity_id):
        r = requests.get(f"{self.api}/search/topic?q={entity_id}&inactive=false")
        try:
            return {
                "type": ["Entity"],
                "id": f"{self.orgbook}/entity/{entity_id}",
                "name": r.json()["results"][0]["names"][0]["text"],
                "registrationNumber": entity_id,
            }
        except:
            raise HTTPException(status_code=400, detail="Couldn't find entity.")

    async def _find_issuer(self, issuer_id):
        issuer_registrations = await AskarStorage().fetch("registration", "issuers")
        issuer = next(
            (
                issuer
                for issuer in issuer_registrations["issuers"]
                if issuer["id"] == issuer_id
            ),
            None,
        )
        if issuer:
            return issuer
        else:
            raise HTTPException(status_code=400, detail="Couldn't find issuer.")
