from config import settings
import requests
from fastapi import HTTPException
from app.utilities import timestamp, verkey_to_multikey
from app.plugins.askar import AskarStorage


class TractionController:
    def __init__(self):
        self.default_kid = "key-01"
        self.endorser_key = settings.TDW_ENDORSER_MULTIKEY
        self.endpoint = settings.TRACTION_API_URL
        self.tenant_id = settings.TRACTION_TENANT_ID
        self.api_key = settings.TRACTION_API_KEY
        self.headers = {}

    def _try_response(self, response, response_key=None):
        try:
            return response.json()[response_key]
        except ValueError:
            print(response.json())
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )

    def authorize(self):
        r = requests.post(
            f"{self.endpoint}/multitenancy/tenant/{self.tenant_id}/token",
            json={"api_key": self.api_key},
        )
        token = self._try_response(r, "token")
        self.headers = {"Authorization": f"Bearer {token}"}

    def resolve(self, did):
        r = requests.post(
            f"{self.endpoint}/multitenancy/tenant/{self.tenant_id}/token",
            json={"api_key": self.api_key},
        )
        token = self._try_response(r, "token")
        self.headers = {"Authorization": f"Bearer {token}"}

    def create_did_key(self):
        r = requests.post(
            f"{self.endpoint}/wallet/did/create",
            headers=self.headers,
            json={"method": "key", "options": {"key_type": "ed25519"}},
        )
        did_info = self._try_response(r, "result")
        return did_info["did"].split(":")[-1]

    def create_did_web(self, did):
        r = requests.post(
            f"{self.endpoint}/wallet/did/create",
            headers=self.headers,
            json={"method": "web", "options": {"did": did, "key_type": "ed25519"}},
        )
        did_info = self._try_response(r, "result")
        return verkey_to_multikey(did_info["verkey"])

    def create_key(self, kid=None):
        r = requests.post(
            f"{self.endpoint}/wallet/keys",
            headers=self.headers,
            json={"kid": kid} if kid else {},
        )
        return self._try_response(r, "multikey")

    def bind_key(self, multikey, kid):
        r = requests.put(
            f"{self.endpoint}/wallet/keys",
            headers=self.headers,
            json={"multikey": multikey, "kid": kid},
        )
        return self._try_response(r, "kid")

    async def sign_vc_jwt(self, document):
        did = document["issuer"]["id"]
        verification_method = f"{did}#{self.default_kid}-jwk"
        r = requests.post(
            f"{self.endpoint}/wallet/jwt/sign",
            headers=self.headers,
            json={
                "did": did,
                "verificationMethod": verification_method,
                "headers": {"typ": "vc+jwt"},
                "payload": document,
            },
        )
        return r.json()

    def issue_vc(self, credential):
        did = credential["issuer"]["id"]
        proof_options = {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-jcs-2022",
            "proofPurpose": "assertionMethod",
            "verificationMethod": f"{did}#{self.default_kid}-multikey",
            "created": timestamp(),
        }
        return self.add_di_proof(credential, proof_options)

    def add_di_proof(self, document, options):
        r = requests.post(
            f"{self.endpoint}/vc/di/add-proof",
            headers=self.headers,
            json={
                "document": document,
                "options": options,
            },
        )
        return self._try_response(r, "securedDocument")

    def endorse(self, document, options):
        options["verificationMethod"] = (
            f"did:key:{self.endorser_key}#{self.endorser_key}"
        )
        r = requests.post(
            f"{self.endpoint}/vc/di/add-proof",
            headers=self.headers,
            json={
                "document": document,
                "options": options,
            },
        )
        return self._try_response(r, "securedDocument")

    def verify_di_proof(self, secured_document):
        r = requests.post(
            f"{self.endpoint}/vc/di/verify",
            headers=self.headers,
            json={
                "securedDocument": secured_document,
            },
        )
        return self._try_response(r, "verified")
