from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .did_document import DidDocument
from config import settings 

class Ressources(BaseModel):
    context: str = Field(example='https://')
    ocaBundle: str = Field(example='https://')
    jsonSchema: str = Field(example='https://')
    vocabulary: str = Field(example='https://')
    governance: str = Field(example='https://')

class CredentialRegistration(BaseModel):
    type: str = Field(example='BCPetroleum&NaturalGasTitle')
    extraTypes: list = Field(example=["DigitalConformityCredential"])
    name: str = Field(example='B.C. Petroleum & Natural Gas Title - DRAFT')
    version: str = Field(example='1.0')
    description: str = Field(example='The majority of subsurface petroleum and natural gas (PNG) resources in British Columbia (B.C.) are owned by the Province. By entering into a tenure agreement with the Province, private industry can develop these resources. Tenure agreements are the mechanism used by the Province to give rights to petroleum and natural gas resources through issuance of Petroleum and Natural Gas Titles.')
    verificationMethod: str = Field(example="did:web:digitaltrust.traceability.site:petroleum-and-natural-gas-act:director-of-petroleum-lands#key-01")
    mappings: Dict[str, str] = Field(example={
        "entityId": "$.credentialSubject.issuedTo.identifier",
        "titleType": "$.credentialSubject.assessments[0].titleType",
        "titleNumber": "$.credentialSubject.assessments[0].titleNumber",
    })
    ressources: Ressources = Field()