from config import settings
from fastapi import HTTPException
import requests
from app.plugins import AskarStorage
from app.plugins.soup import Soup
from app.models import DidDocument, VerificationMethod, Service, Credential
import app.models.untp as untp
from app.models.credential import Issuer
from app.plugins.askar import AskarStorage
from app.plugins.status_list import BitstringStatusList
from app.plugins.traction import TractionController
from app.plugins.orgbook import OrgbookPublisher
from app.plugins.untp import DigitalConformityCredential
from app.utilities import multikey_to_jwk
import uuid
import re
from datetime import datetime, timezone
from jsonpath_ng import jsonpath, parse


class PublisherRegistrar:
    def __init__(self):
        self.tdw_server = settings.TDW_SERVER_URL
        self.publisher_multikey = settings.PUBLISHER_MULTIKEY

    async def register_issuer(self, registration):
        """Register a new issuer with the TDW server."""
        # Derive did path components from registration
        namespace = registration.get("scope").replace(" ", "-").lower()
        identifier = registration.get("name").replace(" ", "-").lower()

        # Request identifier from TDW server
        r = requests.get(
            f"{self.tdw_server}?namespace={namespace}&identifier={identifier}"
        )
        try:
            did = r.json()["didDocument"]["id"]
        except (ValueError, KeyError):
            raise HTTPException(status_code=r.status_code, detail=r.text)

        # Register Authorized key in traction
        default_kid = "key-01"
        multikey_kid = f"{did}#{default_kid}-multikey"
        jwk_kid = f"{did}#{default_kid}-jwk"

        traction = TractionController()
        traction.authorize()
        try:
            authorized_key = traction.get_multikey(did)
            try:
                traction.bind_key(authorized_key, multikey_kid)
            except:
                pass
        except:
            authorized_key = traction.create_did_web(did)
            traction.bind_key(authorized_key, multikey_kid)

        # Create initial DID document
        did_document = DidDocument(
            id=did,
            name=registration.get("name"),
            description=registration.get("description"),
            authentication=[
                multikey_kid,
                jwk_kid,
            ],
            assertionMethod=[
                multikey_kid,
                jwk_kid,
            ],
            verificationMethod=[
                VerificationMethod(
                    id=multikey_kid,
                    type="Multikey",
                    controller=did,
                    publicKeyMultibase=authorized_key,
                ),
                VerificationMethod(
                    id=jwk_kid,
                    type="JsonWebKey",
                    controller=did,
                    publicKeyJwk=multikey_to_jwk(authorized_key),
                ),
            ],
            service=[
                Service(
                    id=f"{did}#orgbook",
                    type="LinkedDomains",
                    serviceEndpoint=settings.ORGBOOK_URL,
                )
            ],
        )

        # Bind an delegated issuing multikey if provided
        if registration.get("multikey"):
            multikey = registration.get("multikey")
            delegated_kid = "key-02"
            delegated_kid_multikey = f"{did}#{delegated_kid}-multikey"
            delegated_kid_jwk = f"{did}#{delegated_kid}-jwk"
            did_document.authentication.append(delegated_kid_multikey)
            did_document.assertionMethod.append(delegated_kid_multikey)
            did_document.verificationMethod.append(
                VerificationMethod(
                    id=delegated_kid_multikey,
                    type="Multikey",
                    controller=did,
                    publicKeyMultibase=multikey,
                )
            )
            did_document.authentication.append(delegated_kid_jwk)
            did_document.assertionMethod.append(delegated_kid_jwk)
            did_document.verificationMethod.append(
                VerificationMethod(
                    id=delegated_kid_jwk,
                    type="JsonWebKey",
                    controller=did,
                    publicKeyJwk=multikey_to_jwk(multikey),
                )
            )

        did_document = did_document.model_dump()

        # Sign DID document
        client_proof_options = r.json()["proofOptions"].copy()
        client_proof_options["verificationMethod"] = (
            f"did:key:{authorized_key}#{authorized_key}"
        )
        signed_did_document = traction.add_di_proof(did_document, client_proof_options)

        # Endorse DID document
        publisher_proof_options = r.json()["proofOptions"].copy()
        publisher_proof_options["verificationMethod"] = (
            f"did:key:{self.publisher_multikey}#{self.publisher_multikey}"
        )
        endorsed_did_document = traction.add_di_proof(
            signed_did_document, publisher_proof_options
        )

        r = requests.post(self.tdw_server, json={"didDocument": endorsed_did_document})
        try:
            log_entry = r.json()["logEntry"]
        except (ValueError, KeyError):
            raise HTTPException(status_code=r.status_code, detail=r.text)
        proof_options = {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-jcs-2022",
            "proofPurpose": "assertionMethod",
            "verificationMethod": f"did:key:{authorized_key}#{authorized_key}",
        }

        # Sign log entry with authorized key
        signed_log_entry = traction.add_di_proof(log_entry, proof_options)
        r = requests.post(
            f"{self.tdw_server}/{namespace}/{identifier}",
            json={"logEntry": signed_log_entry},
        )
        try:
            log_entry = r.json()
        except (ValueError, KeyError):
            raise HTTPException(status_code=r.status_code, detail=r.text)

        return did_document, authorized_key

    async def template_credential(self, credential_registration):
        issuer = await AskarStorage().fetch(
            "issuerRecord", credential_registration["issuer"]
        )
        if not issuer:
            raise HTTPException(status_code=404, detail="Issuer not registered.")
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

        # BCGov template extension, context must be last
        credential_template["@context"].append(
            f"https://{settings.DOMAIN}/contexts/{credential_type}/{credential_version}"
        )
        credential_template["type"].append(credential_type)
        credential_template["credentialSubject"]["type"].append(
            credential_registration["subjectType"]
        )
        return credential_template

        # # Initialize VC
        # credential = Credential(
        #     issuer=Issuer(
        #         id=issuer["id"],
        #         name=issuer["name"],
        #         description=issuer["description"],
        #     )
        # )

        # # UNTP context & type
        # if "untpType" in credential_registration:
        #     # DigitalConformityCredential templating
        #     if credential_registration["untpType"] == "DigitalConformityCredential":
        #         credential.context.append(DigitalConformityCredential().context)
        #         credential.type.append(credential_registration["untpType"])

        #         legal_act_info = Soup(
        #             credential_registration["relatedResources"]["legalAct"]
        #         ).legal_act_info()
        #         legal_act_info = {
        #             "id": legal_act_info["id"],
        #             "name": legal_act_info["title"],
        #             "effectiveDate": legal_act_info["effectiveDate"],
        #         }

        #         credential.credentialSubject = untp.ConformityAttestation(
        #                 assessmentLevel="GovtApproval",
        #                 attestationType="Certification",
        #                 scope=untp.ConformityAssessmentScheme(
        #                     id=credential_registration["relatedResources"][
        #                         "governance"
        #                     ],
        #                     name=f'Governance document for {credential_registration["type"]}',
        #                 ),
        #                 issuedToParty=untp.Party(
        #                     idScheme=untp.IdentifierScheme(
        #                         id="https://www.bcregistry.gov.bc.ca/",
        #                         name="BC Registry",
        #                     )
        #                 ),
        #                 assessment=[
        #                     untp.ConformityAssessment(
        #                         conformityTopic="Governance.Compliance",
        #                         referenceRegulation=untp.Regulation(
        #                             id=legal_act_info["id"],
        #                             name=legal_act_info["name"],
        #                             effectiveDate=legal_act_info["effectiveDate"],
        #                             jurisdictionCountry="CA",
        #                             administeredBy=untp.Party(
        #                                 id="https://gov.bc.ca",
        #                                 name="Government of British Columbia",
        #                             ),
        #                         ),
        #                     )
        #                 ],
        #             ).model_dump()

        # # BCGov context & type
        # credential.context.append(credential_registration["relatedResources"]["context"])
        # credential.type.append(credential_registration["type"])
        # credential.credentialSubject['type'].append(credential_registration["subjectType"])

        # return credential.model_dump()

    async def register_credential(self, credential_registration):
        return await self.template_credential(credential_registration)

    async def format_credential(self, credential, options):
        credential_type = credential.get("type")
        credential_registration = await AskarStorage().fetch(
            "credentialTypeRecord", credential_type
        )
        credential_template = credential_registration.pop("credential_template")
        credential_registration.pop("context")

        entity_id = options.get("entityId")
        cardinality_id = options.get("cardinalityId")

        # Context
        credential["@context"] = credential_template["@context"]

        # Type
        credential["type"] = credential_template["type"]

        # Identifier
        credential_id = options.get("credentialId")
        credential["id"] = f"https://{settings.DOMAIN}/credentials/{credential_id}"

        # Name
        credential["name"] = (
            "BC "
            + " ".join(re.findall("[A-Z][^A-Z]*", credential_type)[2:]).upper().strip()
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
        if credential_registration.get("additional_type"):
            if (
                credential_registration.get("additional_type")
                == "DigitalConformityCredential"
            ):
                if not credential_registration.get("additional_paths"):
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
                for attribute in credential_registration["additional_paths"]:
                    value = options["additionalData"][attribute]
                    path = credential_registration["additional_paths"][attribute]
                    jsonpath_expr = parse(path)
                    jsonpath_expr.update(credential, value)

        # Add BCGov data
        # for attribute in credential_registration['subjectPaths']:
        #     value = credential['credentialSubject'][attribute]
        #     path = credential_registration['subjectPaths'][attribute]
        #     jsonpath_expr = parse(path)
        #     jsonpath_expr.update(credential, value)

        # Refresh Service
        # credential["refreshService"] = [
        #     {
        #         'type': 'SupercessionRefresh',
        #         'id': f'{settings.ORGBOOK_URL}/credentials?type={credential_type}&entityId={entity_id}&cardinalityId={cardinality_id}'
        #     }
        # ]

        # Credential Status
        status_list_id = credential_registration["status_lists"][-1]
        status_list_record = await AskarStorage().fetch(
            "statusListRecord", status_list_id
        )
        credential["credentialStatus"] = [
            (
                {
                    "type": "BitstringStatusListEntry",
                    "statusPurpose": purpose,
                    "statusListIndex": status_list_record["indexes"].pop(),
                    "statusListCredential": f"https://{settings.DOMAIN}/credentials/status/{status_list_id}",
                }
            )
            for purpose in ["revocation", "suspension", "refresh"]
        ]
        await AskarStorage().replace(
            "statusListRecord", status_list_id, status_list_record
        )

        # Validations
        entity_id_path = parse(credential_registration["core_paths"]["entityId"])
        cardinality_id_path = parse(
            credential_registration["core_paths"]["cardinalityId"]
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
            "name": credential["name"],
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
        return credential

    # def publish_credential(self, credential_data):
    #     credential_registration = {}
    #     credential = {
    #         'credentialSubject': {}
    #     }
    #     if 'untpType' in credential_registration:
    #         if credential_registration['untpType'] == 'DigitalConformityCredential':
    #             type = ['ConformityAttestation']
    #             attestationType = "Certification"
    #             assessmentLevel = "GovtApproval"
    #             scope = {
    #                 "id": "https://bcgov.github.io/digital-trust-toolkit/docs/governance/pilots/bc-petroleum-and-natural-gas-title/governance",
    #                 "name": "B.C. Petroleum & Natural Gas Title - DRAFT"
    #             }
    #             issuedToParty = {
    #                 "id": "https://orgbook.gov.bc.ca/entity/A0131571",
    #                 "idScheme": {
    #                     "id": "https://www.bcregistry.gov.bc.ca/",
    #                     "name": "BC Registry",
    #                     "type": "IdentifierScheme"
    #                 },
    #                 "name": "PACIFIC CANBRIAM ENERGY LIMITED",
    #                 "registeredId": credential_data['entityId'],
    #                 "type": [
    #                     "Entity",
    #                 ]
    #             }
    #             assessment = {
    #                 "type": ["ConformityAssessment"],
    #                 "conformityTopic": "Governance.Compliance",
    #                 "compliance": True,
    #                 "referenceRegulation": {
    #                     "administeredBy": {
    #                             "id": "https://www2.gov.bc.ca/gov/content/home",
    #                             "idScheme": {
    #                                 "id": "https://www2.gov.bc.ca/gov/content/home",
    #                                 "name": "BC-GOV",
    #                                 "type": "IdentifierScheme"
    #                             },
    #                         "name": "Government of British Columbia",
    #                         "registeredId": "BC-GOV",
    #                         "type": [
    #                             "Entity"
    #                         ]
    #                     },
    #                     "effectiveDate": act_soup['date'],
    #                     "id": credential_registration['legalAct'],
    #                     "jurisdictionCountry": "CA",
    #                     "name": act_soup['title'],
    #                     "type": [
    #                         "Regulation"
    #                     ]
    #                 }
    #             }
    #             assessedFacility = []
    #             assessedProduct = []
    #             facility = {
    #                 "type": ["Facility"]
    #             }
    #             product = {
    #                 "type": ["Product"]
    #             }

    #         act_soup = {}
