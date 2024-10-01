from fastapi import HTTPException
from config import settings
from datetime import datetime, timezone, timedelta
import requests
import secrets


class AgentController:
    def __init__(self):
        self.endpoint = settings.AGENT_ADMIN_URL
        self.headers = {"X-API-KEY": settings.AGENT_ADMIN_API_KEY}
        self.endorser = settings.ENDORSER_DID
        self.endorser_vm = settings.ENDORSER_VM

    def create_key_pair(self, kid, seed=None):
        r = requests.post(
            f"{self.endpoint}/wallet/keys",
            headers=self.headers,
            json={
                "kid": kid,
                "key_type": "ed25519",
            },
        )
        try:
            return r.json()["multikey"]
        except:
            raise HTTPException(
                status_code=r.status_code, detail="Couldn't create did."
            )

    def register_did(self, did, seed=None):
        # TODO remove this section once seed is optional in acapy
        if not seed:
            seed = secrets.token_hex(16)
        r = requests.post(
            f"{self.endpoint}/did/web",
            headers=self.headers,
            json={
                "id": f"{did}#key-01",
                "key_type": "ed25519",
                "seed": seed,
                "type": "MultiKey",
            },
        )
        try:
            return r.json()["verificationMethod"]
        except:
            raise HTTPException(
                status_code=r.status_code, detail="Couldn't create did."
            )

    def issuer_proof_options(self, verification_method):
        return {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-jcs-2022",
            "proofPurpose": "assertionMethod",
            "verificationMethod": verification_method,
            "created": str(datetime.now(timezone.utc).isoformat("T", "seconds")),
        }

    def endorser_proof_options(self):
        return {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-jcs-2022",
            "verificationMethod": self.endorser_vm,
            "proofPurpose": "authentication",
            "created": str(datetime.now(timezone.utc).isoformat("T", "seconds")),
            "expires": str(
                (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(
                    "T", "seconds"
                )
            ),
        }

    def sign_document(self, document, options):
        r = requests.post(
            f"{self.endpoint}/wallet/di/add-proof",
            headers=self.headers,
            json={"document": document, "options": options},
        )
        try:
            return r.json()["securedDocument"]
        except:
            raise HTTPException(
                status_code=r.status_code, detail="Couldn't sign document."
            )

    def endorse_document(self, document, options):
        options["verificationMethod"] = self.endorser_vm
        r = requests.post(
            f"{self.endpoint}/wallet/di/add-proof",
            headers=self.headers,
            json={"document": document, "options": options},
        )
        try:
            return r.json()["securedDocument"]
        except:
            raise HTTPException(
                status_code=r.status_code, detail="Couldn't endorser document."
            )
