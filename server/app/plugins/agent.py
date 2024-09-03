from quart import current_app, abort
import requests


class Agent:
    def __init__(self):
        self.endorser = current_app.config["ENDORSER_DID"]
        self.endpoint = current_app.config["AGENT_ADMIN_URL"]
        self.headers = {"X-API-KEY": current_app.config["AGENT_ADMIN_API_KEY"]}

    def provision(self):
        body = {
            "id": f"{self.endorser}#multikey",
            "type": "MultiKey",
            "key_type": "ed25519",
            "seed": current_app.config["ENDORSER_SEED"],
        }
        requests.post(f"{self.endpoint}/did/web", headers=self.headers, json=body)

    def register_did(self, did):
        body = {
            "id": f"{did}#multikey",
            "type": "MultiKey",
            "key_type": "ed25519",
            "seed": current_app.config["ENDORSER_SEED"],
        }
        r = requests.post(f"{self.endpoint}/did/web", headers=self.headers, json=body)
        try:
            return r.json()["verificationMethod"]
        except:
            abort(400, "Could not register did")

    def add_di_proof(self, document, options):
        body = {"document": document, "options": options}
        r = requests.post(
            f"{self.endpoint}/wallet/di/add-proof", headers=self.headers, json=body
        )
        try:
            return r.json()["securedDocument"]
        except:
            abort(400, r.text)

    def endorse_document(self, document, options):
        options["verificationMethod"] = f"{self.endorser}#multikey"
        body = {"document": document, "options": options}
        r = requests.post(
            f"{self.endpoint}/wallet/di/add-proof", headers=self.headers, json=body
        )
        try:
            return r.json()["securedDocument"]
        except:
            abort(400, "Could not endorse document")

    def verify_di_proof(self, document):
        body = {"document": document}
        r = requests.post(
            f"{self.endpoint}/wallet/di/verify", headers=self.headers, json=body
        )
        try:
            return r.json()["verificationResponse"]
        except:
            abort(400, "Could not verify di proof")
