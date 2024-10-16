from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from config import settings


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class IssuerRegistration(BaseModel):
    name: str = Field(example="Director of Petroleum Lands")
    scope: str = Field(example="Petroleum and Natural Gas Act")
    description: str = Field(
        example="An officer or employee of the ministry who is designated as the Director of Petroleum Lands by the minister."
    )
    url: str = Field(None, example="https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations/ministries/energy-mines-and-petroleum-resources")
    # image: str = Field(None, example="https://")
    multikey: str = Field(None)

class RelatedResource(BaseModel):
    id: str = Field()
    type: str = Field()

class RelatedResources(BaseModel):
    context: str = Field(example="https://bcgov.github.io/digital-trust-toolkit/contexts/BCPetroleumAndNaturalGasTitle/v1.jsonld")
    legalAct: str = Field(None, example="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/00_96361_01")
    ocaBundle: str = Field(None, example="")
    governance: str = Field(None, example="https://bcgov.github.io/digital-trust-toolkit/docs/governance/pilots/bc-petroleum-and-natural-gas-title")
    

class CredentialRegistration(BaseModel):
    type: str = Field('BCPetroleumAndNaturalGasTitleCredential')
    subjectType: str = Field('PetroleumAndNaturalGasTitle')
    untpType: str = Field(None, example='DigitalConformityCredential')
    version: str = Field(example='v1.0')
    issuer: str = Field(example=f'did:web:{settings.TDW_SERVER_URL.split("//")[-1]}:petroleum-and-natural-gas-act:director-of-petroleum-lands')
    mappings: Dict[str, str] = Field(example={
        "type": "$.credentialSubject.type",
        "titleType": "$.credentialSubject.titleType",
        "titleNumber": '$.credentialSubject.titleNumber',
        "originType": '$.credentialSubject.originType',
        "originNumber": '$.credentialSubject.originNumber',
        "titleHolderType": '$.credentialSubject.issuedToParty.type',
        "titleHolder": '$.credentialSubject.issuedToParty.name',
        "titleHolderInterest": '$.credentialSubject.issuedToParty.interest',
        "titleCaveats": '$.credentialSubject.caveats'
    })
    relatedResources: RelatedResources = Field()

    @field_validator("untpType")
    @classmethod
    def validate_untp_type(cls, value):
        if value not in ['DigitalConformityCredential']:
            raise ValueError(f"Unsupported UNTP type {value}.")
        return value

    @field_validator("relatedResources")
    @classmethod
    def validate_related_resources(cls, value):
        if not value.context:
            raise ValueError("Context is required.")
        # if not value.ocaBundle:
        #     raise ValueError("OCA Bundle is required.")
        return value
