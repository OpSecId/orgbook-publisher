from fastapi import APIRouter, Depends, HTTPException, Request
from config import settings
from app.models import Credential
from app.utilities import freeze_ressource_digest
from app.plugins import AskarStorage, AskarWallet
from app.plugins.status_list import BitstringStatusList
from app.plugins.untp import DigitalConformityCredential
from app.plugins.traction import TractionController

# from .ips import IPSView
import requests
import uuid
from datetime import datetime
from app.utilities import timestamp


class OrgbookPublisher:
    def __init__(self):
        self.api = settings.ORGBOOK_API_URL
        self.orgbook = settings.ORGBOOK_URL
        self.vc_service = settings.ORGBOOK_VC_SERVICE

    def fetch_buisness_info(self, identifier):
        r = requests.get(
            f"{settings.ORGBOOK_API_URL}/search/topic?q={identifier}&inactive=false&revoked=false"
        )
        buisness_info = r.json()["results"][0]
        return {
            "id": f"{settings.ORGBOOK_URL}/entity/{identifier}/type/registration.registries.ca",
            "name": buisness_info["names"][0]["text"],
            "registeredId": identifier,
        }

    async def create_credential_type(self, credential_registration):
        issuer = credential_registration["issuer"]
        verification_method = f"{issuer}#key-01-multikey"
        credential_type = {
            "format": "vc_di",
            "type": credential_registration["type"],
            "issuer": credential_registration["issuer"],
            "version": credential_registration["version"],
            "verificationMethods": [verification_method],
            "ocaBundle": {},
            "topic": {
                "type": "registration.registries.ca",
                "sourceId": {
                    "path": credential_registration["coreMappings"]["entityId"]
                },
            },
            "mappings": [
                {"path": "$.validFrom", "type": "effective_date", "name": "validFrom"},
                {"path": "$.validUntil", "type": "expiry_date", "name": "validUntil"},
            ],
        }
        proof_options = {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-jcs-2022",
            "proofPurpose": "assertionMethod",
            "verificationMethod": verification_method,
        }
        traction = TractionController()
        traction.authorize()
        signed_vc_type = traction.add_di_proof(credential_type, proof_options)
        request_body = {"securedDocument": signed_vc_type}

        r = requests.post(f"{self.vc_service}/credential-types", json=request_body)
        try:
            return r.json()
        except:
            raise HTTPException(
                status_code=400, detail="Couldn't register credential type."
            )

    async def publish_credential(self, credential, credential_registration):
        traction = TractionController()
        traction.authorize()
        vc = traction.issue_vc(credential)
        self.forward_credential(vc, credential_registration)

    async def format_credential(self, data, credential_registration, credential_id):
        entity = self.fetch_buisness_info(data["core"]["entityId"])
        try:
            credential_template = await AskarStorage().fetch(
                "credentialTemplate", credential_registration['type']
            )
        except:
            raise HTTPException(status_code=404, detail="Unknown credential type.")
        credential = credential_template.copy()

        if not data["core"].get("validFrom"):
            data["core"]["validFrom"] = timestamp()

        if not data["core"].get("validUntil"):
            data["core"]["validUntil"] = timestamp(525960)

        credential["validFrom"] = data["core"]["validFrom"]
        credential["validUntil"] = data["core"]["validUntil"]

        # UNTP type and context
        if "untpType" in credential_registration:
            credential["credentialSubject"]["issuedToParty"]["id"] = entity["id"]
            credential["credentialSubject"]["issuedToParty"]["name"] = entity["name"]
            credential["credentialSubject"]["issuedToParty"]["registeredId"] = entity[
                "registeredId"
            ]

            # DigitalConformityCredential template
            if credential_registration["untpType"] == "DigitalConformityCredential":
                for property in data["subject"]:
                    credential["credentialSubject"][property] = data["subject"][
                        property
                    ]

                credential["credentialSubject"]["assessment"][0]["assessedProduct"] = (
                    data["untp"]["assessedProduct"]
                )
                credential["credentialSubject"]["assessment"][0]["assessedFacility"] = (
                    data["untp"]["assessedFacility"]
                )

        credential["credentialStatus"] = [
            await BitstringStatusList().create_entry(
                credential_registration["statusList"][0], "revocation"
            ),
            await BitstringStatusList().create_entry(
                credential_registration["statusList"][0], "update"
            ),
        ]
        credential["id"] = f"https://{settings.DOMAIN}/credentials/{credential_id}"
        return credential

    async def store_credential(self, vc, credential_registration):
        pass

    async def forward_credential(self, vc, credential_registration):
        payload = {
            "securedDocument": vc,
            "options": {
                "format": "vc_di",
                "type": credential_registration["type"],
                "version": credential_registration["version"],
                "credentialId": vc["id"],
            },
        }
        return payload
        r = requests.post(f"{self.vc_service}/credentials", json=payload)
        try:
            return r.json()
        except:
            raise HTTPException(
                status_code=400, detail="Couldn't register credential type."
            )
