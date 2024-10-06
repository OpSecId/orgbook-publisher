import app.models.untp as untp

UNTP_CONTEXTS = {
    "DigitalConformityCredential": "https://test.uncefact.org/vocabulary/untp/dcc/0.4.1/"
}


class DigitalConformityCredential:
    def __init__(self):
        self.context = "https://test.uncefact.org/vocabulary/untp/dcc/0.4.2/"
        self.type = "DigitalConformityCredential"

    def attestation(self, credential_registration=None, products=None, facilities=None):
        conformity_attestation = untp.ConformityAttestation(
            scope = untp.ConformityAssessmentScheme(
                id=credential_registration["relatedResources"]["governance"],
                name=credential_registration["relatedResources"]["governance"],
            ),
            issuedToParty = untp.Party(
                idScheme=untp.IdentifierScheme(
                    id="https://www.bcregistry.gov.bc.ca/",
                    name="BC Registry"
                )
            )
        )
        conformity_attestation.assessment = [self.add_assessment(
            # credential_registration["relatedResources"]["legalAct"],
            # products,
            # facilities,
        )]
        return conformity_attestation

    # def add_subject_party(self, entity_id):
    #     self.credential["credentialSubject"]["issuedTo"] = {"id": entity_id}

    def add_assessment(self, regulation=None, products=[], facilities=[]):
        assessment = untp.ConformityAssessment(
            compliance=True,
            conformityTopic="Governance.Compliance",
            assessmentLevel='GovtApproval',
            attestationType='Certification',
            referenceRegulation=untp.Regulation(
                # id=regulation["id"],
                # name=regulation["name"],
                # effectiveDate=regulation["effectiveDate"],
                jurisdictionCountry="CA",
                administeredBy=untp.Party(
                    id="https://gov.bc.ca",
                    name="Government of British Columbia"
                )
            )
        )
        for product in products:
            assessed_product = untp.Product()
            assessed_product.type.append(product['type'])
            assessment.assessedProduct.append(assessed_product)
        for facility in facilities:
            assessed_facility = untp.Facility()
            assessed_facility.type.append(facility['type'])
            assessment.assessedFacility.append(assessed_facility)
        return assessment
