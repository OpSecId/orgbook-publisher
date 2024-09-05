from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator

BASE_CONTEXT = ''

class VerificationMethod(BaseModel):
    id: str = Field()
    type: str = Field('MultiKey')
    controller: str = Field()
    publicKeyMultibase: str = Field()

class Service(BaseModel):
    id: str = Field()
    type: str = Field()
    serviceEndpoint: str = Field()

class DidDocument(BaseModel):
    context: List[str] = Field([BASE_CONTEXT], alias='@context')
    id: str = Field()
    controller: str = Field()
    authentication: List[Union[str, VerificationMethod]] = Field()
    assertionMethod: List[Union[str, VerificationMethod]] = Field()
    verificationMethod: List[VerificationMethod] = Field()
    service: List[Service] = Field()