from config import settings
from fastapi import HTTPException
import requests
from app.plugins import AskarStorage
from app.plugins.soup import Soup
from app.models import DidDocument, VerificationMethod, Service, Credential
import app.models.untp as untp
from app.models.credential import Issuer
from app.plugins.askar import AskarStorage
from app.plugins.traction import TractionController
from app.plugins.untp import DigitalConformityCredential
from app.utilities import multikey_to_jwk


class PublisherRegistrar:
    def __init__(self):
        self.tdw_server = settings.TDW_SERVER_URL
        self.endorser_multikey = settings.TDW_ENDORSER_MULTIKEY

    async def register_issuer(self, name, scope, url, description, multikey=None):
        namespace = scope.replace(" ", "-").lower()
        identifier = name.replace(" ", "-").lower()
        default_kid = "key-01"

        # Request identifier from TDW server
        r = requests.get(
            f"{self.tdw_server}?namespace={namespace}&identifier={identifier}"
        )
        try:
            did = r.json()["didDocument"]["id"]
        except (ValueError, KeyError):
            raise HTTPException(status_code=r.status_code, detail=r.text)

        # Register Authorized key in traction
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

        did_document = DidDocument(
            id=did,
            name=name,
            description=description,
            authentication=[multikey_kid],
            assertionMethod=[multikey_kid],
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
            ]
        )

        # Bind an issuing multikey if provided
        if multikey:
            did_document.verificationMethod.append(
                VerificationMethod(
                    id=f"{did}#key-02-multikey",
                    type="Multikey",
                    controller=did,
                    publicKeyMultibase=multikey,
                )
            )

        did_document = did_document.model_dump()

        client_proof_options = r.json()["proofOptions"].copy()
        client_proof_options["verificationMethod"] = (
            f"did:key:{authorized_key}#{authorized_key}"
        )
        signed_did_document = traction.add_di_proof(did_document, client_proof_options)

        endorser_proof_options = r.json()["proofOptions"].copy()
        endorser_proof_options["verificationMethod"] = (
            f"did:key:{self.endorser_multikey}#{self.endorser_multikey}"
        )
        endorsed_did_document = traction.add_di_proof(
            signed_did_document, endorser_proof_options
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
        signed_log_entry = traction.add_di_proof(log_entry, proof_options)
        r = requests.post(
            f"{self.tdw_server}/{namespace}/{identifier}",
            json={"logEntry": signed_log_entry},
        )
        try:
            log_entry = r.json()
        except (ValueError, KeyError):
            raise HTTPException(status_code=r.status_code, detail=r.text)
        
        await AskarStorage().replace("issuer", did_document["id"], did_document)
        await AskarStorage().replace("authorizedKey", did_document["id"], authorized_key)
        return did_document

    async def template_credential(self, credential_registration):
        issuer = await AskarStorage().fetch("issuer", credential_registration["issuer"])

        # Initialize VC
        credential = Credential(
            issuer=Issuer(
                id=issuer["id"],
                name=issuer["name"],
                description=issuer["description"],
            )
        )

        # UNTP context & type
        if "untpType" in credential_registration:
            # DigitalConformityCredential templating
            if credential_registration["untpType"] == "DigitalConformityCredential":
                credential.context.append(DigitalConformityCredential().context)
                credential.type.append(credential_registration["untpType"])

                legal_act_info = Soup(
                    credential_registration["relatedResources"]["legalAct"]
                ).legal_act_info()
                legal_act_info = {
                    "id": legal_act_info["id"],
                    "name": legal_act_info["title"],
                    "effectiveDate": legal_act_info["effectiveDate"],
                }

                credential.credentialSubject = untp.ConformityAttestation(
                        assessmentLevel="GovtApproval",
                        attestationType="Certification",
                        scope=untp.ConformityAssessmentScheme(
                            id=credential_registration["relatedResources"][
                                "governance"
                            ],
                            name=f'Governance document for {credential_registration["type"]}',
                        ),
                        issuedToParty=untp.Party(
                            idScheme=untp.IdentifierScheme(
                                id="https://www.bcregistry.gov.bc.ca/",
                                name="BC Registry",
                            )
                        ),
                        assessment=[
                            untp.ConformityAssessment(
                                conformityTopic="Governance.Compliance",
                                referenceRegulation=untp.Regulation(
                                    id=legal_act_info["id"],
                                    name=legal_act_info["name"],
                                    effectiveDate=legal_act_info["effectiveDate"],
                                    jurisdictionCountry="CA",
                                    administeredBy=untp.Party(
                                        id="https://gov.bc.ca",
                                        name="Government of British Columbia",
                                    ),
                                ),
                            )
                        ],
                    ).model_dump()

        # BCGov context & type
        credential.context.append(credential_registration["relatedResources"]["context"])
        credential.type.append(credential_registration["type"])
        credential.credentialSubject['type'].append(credential_registration["subjectType"])

        return credential.model_dump()

    async def register_credential(self, credential_registration):
        return await self.template_credential(credential_registration)

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
