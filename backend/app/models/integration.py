from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from config import settings


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


EXAMPLE_ISSUER = "did:web:example.com:integration:director-of-petroleum-lands"


class IssuerRegistration(BaseModel):
    name: str = Field(example="Director of Petroleum Lands")
    scope: str = Field(example="Petroleum and Natural Gas Act")
    description: str = Field(
        example="Director of Petroleum Lands as defined in the Petroleum and Natural Gas Act."
    )


class CorePaths(BaseModel):
    entityId: str = Field()
    cardinalityId: str = Field()


class RelatedResources(BaseModel):
    context: str = Field()
    legalAct: str = Field(None)
    ocaBundle: str = Field(None)
    governance: str = Field(None)


class CredentialRegistration(BaseModel):
    type: str = Field("BCPetroleumAndNaturalGasTitleCredential")
    version: str = Field(example="v1")
    issuer: str = Field(None, example=EXAMPLE_ISSUER)
    corePaths: CorePaths = Field(
        example={
            "entityId": "$.credentialSubject.issuedToParty.registeredId",
            "cardinalityId": "$.credentialSubject.titleNumber",
        }
    )
    subjectType: str = Field(None, example="PetroleumAndNaturalGasTitle")
    subjectPaths: Dict[str, str] = Field(
        example={
            "titleType": "$.credentialSubject.titleType",
            "titleNumber": "$.credentialSubject.titleNumber",
            "originType": "$.credentialSubject.originType",
            "originNumber": "$.credentialSubject.originNumber",
        }
    )
    additionalType: str = Field(None, example="DigitalConformityCredential")
    additionalPaths: Dict[str, str] = Field(
        None,
        example={
            "wells": "$.credentialSubject.assessment[0].assessedFacility",
            "tracts": "$.credentialSubject.assessment[0].assessedProduct",
        },
    )
    relatedResources: RelatedResources = Field(
        example={
            "context": "https://bcgov.github.io/digital-trust-toolkit/contexts/BCPetroleumAndNaturalGasTitle/v1.jsonld",
            "governance": "https://bcgov.github.io/digital-trust-toolkit/docs/governance/pilots/bc-petroleum-and-natural-gas-title/",
            "legalAct": "https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/00_96361_01",
        }
    )


class CredentialSubject(BaseModel):
    type: str = Field()


class PublicationCredential(BaseModel):
    validFrom: str = Field(None, example="2024-11-11T00:00:00Z")
    validUntil: str = Field(None, example="2025-11-11T00:00:00Z")
    credentialSubject: dict = Field(
        example={
            "titleType": "NaturalGasLease",
            "titleNumber": "65338",
            "originType": "DrillingLicense",
            "originNumber": "42566",
        }
    )


class PublicationOptions(BaseModel):
    # CANADA NORTHWEST ENERGY LIMITED
    entityId: str = Field(example="A0131571")
    cardinalityId: str = Field(example="65338")
    additionalData: dict = Field(
        None,
        example={
            "wells": [
                {"type": ["Facility", "Well"], "id": "urn:code:uwi:", "name": ""}
            ],
            "tracts": [
                {
                    "type": ["Product", "Tract"],
                    "id": "urn:code:hs:",
                    "name": "",
                    "zones": [],
                    "notes": [],
                    "rights": [],
                }
            ],
        },
    )


class Publication(BaseModel):
    credential: PublicationCredential = Field()
    options: PublicationOptions = Field()


class RequestSecret(BaseModel):
    client_id: str = Field(example=EXAMPLE_ISSUER)


class RequestToken(BaseModel):
    client_id: str = Field(example=EXAMPLE_ISSUER)
    client_secret: str = Field(example="s3cret_key")
