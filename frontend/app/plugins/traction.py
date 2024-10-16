from flask import current_app
from datetime import datetime
import random
import requests
import json


class TractionController:
    def __init__(self, token=None):
        self.endpoint = current_app.config['TRACTION_API_URL']
        self.tenant_id = current_app.config['TRACTION_TENANT_ID']
        self.api_key = current_app.config['TRACTION_API_KEY']
        self.headers = {
            "Authorization": f"Bearer {token}"
        }
        
    def make_post(self, endpoint, body):
        r = requests.post(
            endpoint, 
            headers=self.headers, 
            json=body
        )
        try:
            return r.json()
        except:
            pass
        
    def request_token(self):
        r = requests.post(
            f'{self.endpoint}/multitenancy/tenant/{self.tenant_id}/token',
            json={"api_key": self.api_key}
        )
        return r.json()['token']
        
    def new_presentation_request(self):
        attributes = ["permissions", "email", "id", "credentialType"]
        schema_id = 'Mo2T76ZKcQvdYNPdgGbMFi:2:Delegated Issuing Entity:0.1'
        cred_def_id = "Mo2T76ZKcQvdYNPdgGbMFi:3:CL:2074989:Delegated Issuing Entity"
        presentation_request={
            "name": "Orgbook Publisher Authorization",
            "version": "1.0",
            "nonce": str(random.randrange(10000000, 99999999, 8)),
            "requested_attributes": {
                "issuerInfo": {
                    "names": attributes,
                    "restrictions":[
                        {
                            "cred_def_id": cred_def_id
                        }
                    ]
                }
            },
            "requested_predicates": {}
        }
        print(json.dumps(presentation_request, indent=2))
        presentation_request = {
            "presentation_request": {
                "indy": presentation_request
            }
        }
        # timestamp = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        # presentation_request['non_revoked'] = {
        #     "from": 123,
        #     "to": 123
        # }
        r = self.make_post(
            f'{self.endpoint}/present-proof-2.0/create-request', 
            presentation_request
        )
        
        pres_ex_id = r['pres_ex_id']
        oob_invitation = {
            "attachments": [
                {
                    "id": pres_ex_id,
                    "type": "present-proof"
                }
            ]
        }
        r = self.make_post(
            f'{self.endpoint}/out-of-band/create-invitation', 
            oob_invitation
        )
        return r['invitation']