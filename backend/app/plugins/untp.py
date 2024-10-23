import app.models.untp as untp

UNTP_CONTEXTS = {
    "DigitalConformityCredential": "https://test.uncefact.org/vocabulary/untp/dcc/0.5.0/"
}


class DigitalConformityCredential:
    def __init__(self):
        self.context = "https://test.uncefact.org/vocabulary/untp/dcc/0.5.0/"
        self.type = "DigitalConformityCredential"

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
            compliance=True,
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
