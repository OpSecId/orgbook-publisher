from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .did_document import DidDocument
from config import settings 

class Ressources(BaseModel):
    context: str = Field(example='https://raw.githubusercontent.com/bcgov/digital-trust-toolkit/main/docs/governance/pilots/bc-petroleum-and-natural-gas-title/context.jsonld')
    # ocaBundle: str = Field(example='https://')
    # jsonSchema: str = Field(example='https://')
    vocabulary: str = Field(example='https://bcgov.github.io/digital-trust-toolkit/docs/governance/pilots/bc-petroleum-and-natural-gas-title/vocabulary')
    governance: str = Field(example='https://bcgov.github.io/digital-trust-toolkit/docs/governance/pilots/bc-petroleum-and-natural-gas-title/governance')

class CredentialRegistration(BaseModel):
    type: str = Field(example='BCPetroleum&NaturalGasTitle')
    extraTypes: list = Field(example=["DigitalConformityCredential"])
    name: str = Field(example='B.C. Petroleum & Natural Gas Title - DRAFT')
    version: str = Field(example='v0.1')
    description: str = Field(example='The majority of subsurface petroleum and natural gas (PNG) resources in British Columbia (B.C.) are owned by the Province. By entering into a tenure agreement with the Province, private industry can develop these resources. Tenure agreements are the mechanism used by the Province to give rights to petroleum and natural gas resources through issuance of Petroleum and Natural Gas Titles.')
    verificationMethod: str = Field(example="did:web:digitaltrust.traceability.site:petroleum-and-natural-gas-act:director-of-petroleum-lands#key-01")
    mappings: Dict[str, str] = Field(example={
        "entityId": "$.credentialSubject.issuedToParty.registeredId",
        "entityName": "$.credentialSubject.issuedToParty.legalName",
        "titleType": "$.credentialSubject.titleType",
        "titleNumber": "$.credentialSubject.titleNumber",
    })
    ressources: Ressources = Field()
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)