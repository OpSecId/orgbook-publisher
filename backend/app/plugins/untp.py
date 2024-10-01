import app.models.untp as untp
from untp_models.conformity_credential import ConformityAttestation, ConformityAssessment, Regulation, Entity, Product, Facility

UNTP_CONTEXTS = {
    "DigitalConformityCredential": "https://test.uncefact.org/vocabulary/untp/dcc/0.4.1/"
}


class DigitalConformityCredential:
    def __init__(self):
        self.context = "https://test.uncefact.org/vocabulary/untp/dcc/0.4.1"
        self.type = "DigitalConformityCredential"

    def vc_to_dcc(self, credential_subject, credential_registration):
        conformity_attestation = ConformityAttestation(
            type=[],
        )
        credential_subject["assessments"]["type"].append("ConformityAttestation")
        credential_subject["assessments"]["issuedToParty"]["idScheme"] = {
            "type": ["IdentifierScheme"],
            "id": "https://www.bcregistry.gov.bc.ca/",
            "name": "BC Registry",
        }
        credential_subject["assessments"]["assessmentLevel"] = "GovtApproval"
        credential_subject["assessments"]["attestationType"] = "Certification"
        credential_subject["assessments"]["scope"] = {
            "id": credential_registration["relatedResources"]["governance"]["id"],
            "name": credential_registration["relatedResources"]["governance"]["name"],
        }
        for idx, assessment in enumerate(credential_subject["assessments"]):
            credential_subject["assessments"][idx] = ConformityAssessment(
                referenceRegulation=Regulation(
                    id=credential_registration["relatedResources"]["legalAct"]["id"],
                    name=credential_registration["relatedResources"]["legalAct"]["name"],
                    jurisdictionCountry="CA",
                    administeredBy=Entity(
                        id="https://gov.bc.ca",
                        name="Government of British Columbia"
                    )
                ),
                compliance=True,
                conformityTopic="Governance.Compliance",
                assessedProducts=[
                    Product() for product in assessment['assessedProducts']
                ],
                assessedFacilities=[
                    Facility() for facility in assessment['assessedFacilities']
                ],
            )
        return credential_subject

    def add_subject_party(self, entity_id):
        self.credential["credentialSubject"]["issuedTo"] = {"id": entity_id}

    def add_assessment(self, credential, assessment):
        credential["credentialSubject"]["assessments"] = [assessment]
        return credential
