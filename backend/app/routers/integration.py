from typing import Annotated
from jsonpath_ng import jsonpath, parse
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.registrations import CredentialRegistration
from app.models.credential import Credential, Issuer
import app.models.untp as untp
from config import settings
from app.plugins import AskarStorage, DigitalConformityCredential, Soup
from app.security import check_api_key_header

router = APIRouter(prefix="/integration", tags=["Integration"])


@router.post("/register-credential")
async def register_credential_integration(
    request_body: CredentialRegistration, authorized=Depends(check_api_key_header)
):
    credential_registration = request_body.model_dump()
    # issuer = await AskarStorage().fetch('issuer', credential_registration['issuer'])
    issuer = Issuer(
        id=credential_registration["issuer"],
    )

    # W3C type and context
    contexts = ["https://www.w3.org/ns/credentials/v2"]
    types = ["VerifiableCredential"]
    # credential_subject = {'type': []}

    # UNTP type and context
    if "untpType" in credential_registration:
        # credential_subject = {}

        # DigitalConformityCredential template
        if credential_registration["untpType"] == "DigitalConformityCredential":
            contexts.append(DigitalConformityCredential().context)
            types.append(credential_registration["untpType"])

            legal_act_info = Soup(
                credential_registration["relatedResources"]["legalAct"]
            ).legal_act_info()

            # credential_subject = credential_subject | untp.ConformityAttestation(
            credential_subject = (
                {}
                | untp.ConformityAttestation(
                    assessmentLevel="GovtApproval",
                    attestationType="Certification",
                    scope=untp.ConformityAssessmentScheme(
                        id=credential_registration["relatedResources"]["governance"],
                        name=f'Governance document for {credential_registration["type"]}',
                    ),
                    issuedToParty=untp.Party(
                        idScheme=untp.IdentifierScheme(
                            id="https://www.bcregistry.gov.bc.ca/", name="BC Registry"
                        )
                    ),
                    assessment=[
                        untp.ConformityAssessment(
                            compliance=True,
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
            )

    # BCGov type and context
    contexts.append(credential_registration["relatedResources"]["context"])
    types.append(credential_registration["type"])
    credential_subject["type"].append(credential_registration["subjectType"])

    credential_template = Credential(
        context=contexts,
        type=types,
        issuer=issuer,
        credentialSubject=credential_subject,
    ).model_dump()

    # for mapping in credential_registration['mappings']:
    #     path_array = credential_registration['mappings'][mapping].split('.')
    #     path_end = credential_registration['mappings'][mapping].split('.')[-1]
    #     tmp_path = credential_registration['mappings'][mapping].rstrip(f'.{path_end}')
    #     jsonpath_expr = parse(tmp_path)
    #     jsonpath_expr.update(credential_template, {path_end: 'PLACEHOLDER'})
    #     # print(mapping)

    return JSONResponse(status_code=200, content=credential_template)
