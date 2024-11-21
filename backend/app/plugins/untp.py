import app.models.untp as untp
from app.plugins.soup import Soup

UNTP_CONTEXTS = {
    "DigitalConformityCredential": "https://test.uncefact.org/vocabulary/untp/dcc/0.5.0/"
}


class DigitalConformityCredential:
    def __init__(self):
        self.type = "DigitalConformityCredential"
        self.context = UNTP_CONTEXTS[self.type]

    def get_legal_act_info(self, legal_act_url):
        legal_act_info = Soup(legal_act_url).legal_act_info()
        legal_act_info = {
            "id": legal_act_info["id"],
            "name": legal_act_info["title"],
            "effectiveDate": legal_act_info["effectiveDate"],
        }
        return legal_act_info

    def extend_template(self, credential_registration, credential_template):
        if not credential_registration.get("relatedResources").get("legalAct"):
            pass
        if not credential_registration.get("relatedResources").get("governance"):
            pass

        credential_template["@context"].append(self.context)
        credential_template["type"].append(self.type)

        legal_act_info = self.get_legal_act_info(
            legal_act_url=credential_registration["relatedResources"]["legalAct"]
        )

        credential_template["credentialSubject"] = untp.ConformityAttestation(
            assessmentLevel="GovtApproval",
            attestationType="Certification",
            scope=untp.ConformityAssessmentScheme(
                id=credential_registration["relatedResources"]["governance"],
                name=f'{credential_registration["type"]} Governance Document',
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
        return credential_template

    def attestation(self, scope, regulation, products=None, facilities=None):
        conformity_attestation = untp.ConformityAttestation(
            assessmentLevel="GovtApproval",
            attestationType="Certification",
            scope=untp.ConformityAssessmentScheme(
                id=scope["id"],
                name=scope["name"],
            ),
            issuedToParty=untp.Party(
                idScheme=untp.IdentifierScheme(
                    id="https://www.bcregistry.gov.bc.ca/", name="BC Registry"
                )
            ),
        )
        # conformity_attestation.assessment = [self.add_assessment(
        #     regulation,
        #     # products,
        #     # facilities,
        # )]
        return conformity_attestation

    # def add_subject_party(self, entity_id):
    #     self.credential["credentialSubject"]["issuedTo"] = {"id": entity_id}

    def add_assessment(self, regulation=None, products=[], facilities=[]):
        assessment = untp.ConformityAssessment(
            conformityTopic="Governance.Compliance",
            referenceRegulation=untp.Regulation(
                id=regulation["id"],
                name=regulation["name"],
                effectiveDate=regulation["effectiveDate"],
                jurisdictionCountry="CA",
                administeredBy=untp.Party(
                    id="https://gov.bc.ca", name="Government of British Columbia"
                ),
            ),
        )
        for product in products:
            assessed_product = untp.Product()
            assessed_product.type.append(product["type"])
            assessment.assessedProduct.append(assessed_product)
        for facility in facilities:
            assessed_facility = untp.Facility()
            assessed_facility.type.append(facility["type"])
            assessment.assessedFacility.append(assessed_facility)
        return assessment
