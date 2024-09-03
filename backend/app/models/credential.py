from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator

BASE_CONTEXT = ''

class Issuer(BaseModel):
    id: str = Field()
    name: str = Field(None)
    description: str = Field(None)

class Credential(BaseModel):
    context: List[str] = Field([BASE_CONTEXT], alias='@context')
    type: List[str] = Field(['VerifiableCredential'])
    id: str = Field()
    issuer: Issuer = Field()
    name: str = Field(None)
    description: str = Field(None)
    credentialSubject: Union[dict, List[dict]] = Field(None)
    credentialStatus: Union[dict, List[dict]] = Field([])
    credentialSchema: Union[dict, List[dict]] = Field([])
    termsOfUse: Union[dict, List[dict]] = Field([])
    renderMethod: Union[dict, List[dict]] = Field([])