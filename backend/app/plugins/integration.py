from fastapi import HTTPException
from config import settings
from app.plugins import AskarStorage, BitstringStatusList
import uuid
from datetime import datetime, timezone
from aries_askar.error import AskarError
from app.plugins.qrcode import create_qr_code
from app.plugins.untp import DigitalConformityCredential
from app.plugins.orgbook import OrgbookPublisher
from jsonpath_ng import jsonpath, parse
import time
import jwt
import secrets
import random


class IntegrationModule:
    def __init__(self):
        self.issuer = f"did:key:{settings.PUBLISHER_MULTIKEY}"

    async def create_client_secret(self, client_id):
        askar = AskarStorage()
        did_document = await askar.fetch("integration:issuer", client_id)
        if not did_document:
            raise HTTPException(status_code=404, detail="Client not found")
        client_secret = secrets.token_urlsafe(64)
        await askar.replace("integration:secret", client_id, client_secret)
        return client_secret

    async def request_token(self, client_id, client_secret):
        askar = AskarStorage()

        if client_secret != await askar.fetch("integration:secret", client_id):
            raise HTTPException(status_code=400, detail="Bad request")

        payload = {"client_id": client_id, "expires": int(time.time()) + 600}
        access_token = jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )
        return access_token

    async def create_did_document(self, registration):
        namespace = registration.get("scope").replace(" ", "-").lower()
        namespace = "integration"
        identifier = registration.get("name").replace(" ", "-").lower()
        did = f"did:web:{settings.DOMAIN}:{namespace}:{identifier}"
        did_document = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://www.w3.org/ns/credentials/v2",
            ],
            "id": did,
            "name": registration.get("name"),
            "description": registration.get("description"),
            "service": [
                {
                    "id": f"{did}#orgbook",
                    "type": "LinkedDomain",
                    "serviceEndpoint": settings.ORGBOOK_URL,
                }
            ],
        }
        askar = AskarStorage()
        try:
            await askar.store("integration:issuer", did_document["id"], did_document)
        except AskarError:
            did_document = await askar.fetch("integration:issuer", did_document["id"])
        return did_document

    async def create_delegated_issuer_credential(self, did_document):
        credential_id = str(uuid.uuid4())
        credential = {
            "@context": ["https://www.w3.org/ns/credentials/v2"],
            "type": ["VerifiableCredential", "DelegatedIssuerCredential"],
            "id": f"urn:uuid:{credential_id}",
            "name": "Delegated Orgbook Issuer",
            "issuer": {
                "id": self.issuer,
                "name": "BC Orgbook Publisher",
                "image": "https://avatars.githubusercontent.com/u/916280",
            },
            "validFrom": datetime.now(timezone.utc).isoformat("T", "seconds"),
            "validUntil": datetime.now(timezone.utc).isoformat("T", "seconds"),
            "credentialSubject": {
                "id": did_document["id"],
                "name": did_document["name"],
            },
        }
        tags = {"type": "DelegatedIssuerCredential"}
        await AskarStorage().store(
            "integration:credential", credential_id, credential, tags=tags
        )
        pickup_qr_code = create_qr_code(
            f"https://{settings.DOMAIN}/credentials/{credential_id}"
        )
        return pickup_qr_code

    async def create_credential_type(self, credential_registration):
        # Fetch issuer information
        issuer = await AskarStorage().fetch(
            "integration:issuer", credential_registration["issuer"]
        )
        credential_type = credential_registration["type"]
        credential_version = credential_registration["version"]

        # Create base credential template
        credential_template = {
            "@context": ["https://www.w3.org/ns/credentials/v2"],
            "type": ["VerifiableCredential"],
            "issuer": {
                "id": issuer["id"],
                "name": issuer["name"],
                "description": issuer["description"],
            },
            "credentialSubject": {"type": []},
        }

        if credential_registration.get("additionalType"):
            # Extend credential template
            if (
                credential_registration.get("additionalType")
                == "DigitalConformityCredential"
            ):
                credential_template = DigitalConformityCredential().extend_template(
                    credential_registration=credential_registration,
                    credential_template=credential_template,
                )

        # Create new BitstringStatusList credential
        indexes = list(range(200000))
        random.shuffle(indexes)
        status_list_id = str(uuid.uuid4())
        status_list_credential = await BitstringStatusList().create(
            id=f"https://{settings.DOMAIN}/credentials/status/{status_list_id}",
            issuer={"id": credential_registration["issuer"]},
            purpose=["revocation", "suspension", "supercession"],
            length=len(indexes),
        )
        credential_registration["statusList"] = [status_list_id]

        # BCGov template extension, context must be last
        credential_template["@context"].append(
            f"https://{settings.DOMAIN}/contexts/{credential_type}/{credential_version}"
        )
        credential_template["type"].append(credential_type)
        credential_template["credentialSubject"]["type"].append(
            credential_registration["subjectType"]
        )

        await AskarStorage().store("statusListIndexes", status_list_id, indexes)
        await AskarStorage().store(
            "statusListCredential", status_list_id, status_list_credential
        )
        # Cache context redirect
        await AskarStorage().replace(
            "integration:context",
            f"{credential_type}/{credential_version}",
            credential_registration.get("relatedResources").get("context"),
        )
        await AskarStorage().replace(
            "integration:credentialType",
            credential_type,
            credential_registration,
        )
        await AskarStorage().replace(
            "integration:credentialTemplate",
            credential_type,
            credential_template,
        )
        return credential_template

    async def publish_credential(self, credential, options):
        credential_type = credential["type"]
        credential_registration = await AskarStorage().fetch(
            "integration:credentialType", credential_type
        )
        credential_template = await AskarStorage().fetch(
            "integration:credentialTemplate", credential_type
        )

        entity_id = options.get("entityId")
        cardinality_id = options.get("cardinalityId")

        # Context
        credential["@context"] = credential_template["@context"]

        # Type
        credential["type"] = credential_template["type"]

        # Identifier
        credential_id = str(uuid.uuid4())
        credential["id"] = (
            f"https://{settings.DOMAIN}/integration/credentials/{credential_id}"
        )

        # Issuer
        credential["issuer"] = credential_template["issuer"]

        # Validity Period
        credential["validFrom"] = credential.get("validFrom") or datetime.now(
            timezone.utc
        ).isoformat("T", "seconds")
        credential["validUntil"] = credential.get("validUntil") or datetime.now(
            timezone.utc
        ).isoformat("T", "seconds")

        # Credential Subject
        credential["credentialSubject"] |= credential_template["credentialSubject"]
        if credential_registration.get("additionalType"):
            if (
                credential_registration.get("additionalType")
                == "DigitalConformityCredential"
            ):
                if not credential_registration.get("additionalPaths"):
                    pass

                # Add issuedToParty information based on Orgbook entity data
                entity = OrgbookPublisher().fetch_buisness_info(entity_id)
                credential["credentialSubject"]["issuedToParty"]["id"] = entity["id"]
                credential["credentialSubject"]["issuedToParty"]["name"] = entity[
                    "name"
                ]
                credential["credentialSubject"]["issuedToParty"]["registeredId"] = (
                    entity_id
                )

                # Add assessed data (product & facility)
                for attribute in credential_registration["additionalPaths"]:
                    value = options["additionalData"][attribute]
                    path = credential_registration["additionalPaths"][attribute]
                    jsonpath_expr = parse(path)
                    jsonpath_expr.update(credential, value)

        # Add BCGov data
        # for attribute in credential_registration['subjectPaths']:
        #     value = credential['credentialSubject'][attribute]
        #     path = credential_registration['subjectPaths'][attribute]
        #     jsonpath_expr = parse(path)
        #     jsonpath_expr.update(credential, value)

        # Credential Status
        purpose = ["revocation", "suspension", "supercession"]
        credential["credentialStatus"] = [
            (
                await BitstringStatusList().create_entry(
                    credential_registration["statusList"][-1], status
                )
            )
            for status in purpose
        ]

        # Refresh Service
        # credential["refreshService"] = [
        #     {
        #         'type': 'SupercessionRefresh',
        #         'id': f'{settings.ORGBOOK_URL}/credentials?type={credential_type}&entityId={entity_id}&cardinalityId={cardinality_id}'
        #     }
        # ]

        # Validations
        entity_id_path = parse(credential_registration["corePaths"]["entityId"])
        cardinality_id_path = parse(
            credential_registration["corePaths"]["cardinalityId"]
        )
        if [match.value for match in entity_id_path.find(credential)][0] != entity_id:
            pass
        if [match.value for match in cardinality_id_path.find(credential)][
            0
        ] != cardinality_id:
            pass
        if credential["issuer"]["id"] != credential_registration["issuer"]:
            pass

        credential = {
            "@context": credential["@context"],
            "type": credential["type"],
            "id": credential["id"],
            "issuer": credential["issuer"],
            "validFrom": credential["validFrom"],
            "validUntil": credential["validUntil"],
            "credentialSubject": credential["credentialSubject"],
            # 'credentialSchema': credential['credentialSchema'],
            "credentialStatus": credential["credentialStatus"],
            # 'renderMethod': credential['renderMethod'],
            # 'refreshService': credential['refreshService'],
            # 'termsOfUse': credential['termsOfUse'],
        }

        # Proof
        # kid = credential['issuer']['id']+'#key-01-multikey'

        # traction = TractionController()
        # traction.authorize()
        # # VC Data Integrity
        # vc = traction.issue_vc(credential)
        # # Optional, transforms array of 1 proof into a proof object
        # vc['proof'] = vc['proof'][0]
        # vc = credential
        # VC JOSE
        # vc_jwt = traction.sign_vc_jwt(vc)
        # vc = credential
        # vc_jwt = credential

        # tags = {
        #     'type': credential_type,
        #     'entity_id': entity_id,
        #     'cardinality_id': cardinality_id,
        #     'supersession': 0,
        #     'revocation': 0,
        #     'suspension': 0
        # }

        # record = tags | {
        #     'vc': vc,
        #     'vc_jwt': vc_jwt,
        # }

        # await AskarStorage().store("integration:application/vc", credential_id, vc, tags=tags)
        # await AskarStorage().store("integration:application/vc+jwt", credential_id, vc_jwt, tags=tags)

        return credential
