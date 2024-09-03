from quart import current_app, abort
from app.plugins import Agent
import requests
import uuid


class TrustedWebClient:
    def __init__(self):
        self.endpoint = current_app.config["TRUST_SERVER_URL"]
        self.endorser = current_app.config["ENDORSER_DID"]

    def request_identifier(self, identifier):
        r = requests.get(f'{self.endpoint}/{identifier}')
        try:
            return r.json()
        except:
            abort(400, "Identifier not available.")

    def register_identifier(self, identifier):
        identifier_request = self.request_identifier(identifier)
        did_doc = identifier_request["document"]
        proof_options = identifier_request["options"]

        verification_method = Agent().register_did(did_doc["id"])

        did_doc["verificationMethod"].append(verification_method)
        proof_options["verificationMethod"] = verification_method["id"]
        proof_options['id'] = f'urn:uuid:{str(uuid.uuid4())}'

        signed_did_doc = Agent().add_di_proof(did_doc, proof_options)

        proof_options['verificationMethod'] = current_app.config["ENDORSER_DID"]+'#multikey'
        proof_options['previousProof'] = proof_options.pop('id')
        endorsed_did_doc = Agent().add_di_proof(signed_did_doc, proof_options)

        r = requests.post(
            f'{self.endpoint}/{identifier}',
            json={"didDocument": endorsed_did_doc},
        )
        try:
            return r.json()
        except:
            abort(400, "Identifier not available.")
