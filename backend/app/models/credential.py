from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .di_proof import DataIntegrityProof

class Issuer(BaseModel):
    id: str = Field()
    name: str = Field(None)
    description: str = Field(None)

class Credential(BaseModel):
    context: List[str] = Field(['https://www.w3.org/ns/credentials/v2'], alias='@context')
    type: List[str] = Field(['VerifiableCredential'])
    id: str = Field()
    issuer: Issuer = Field()
    name: str = Field(None)
    description: str = Field(None)
    credentialSubject: Union[dict, List[dict]] = Field(None)
    credentialStatus: Union[dict, List[dict]] = Field(None)
    credentialSchema: Union[dict, List[dict]] = Field(None)
    termsOfUse: Union[dict, List[dict]] = Field(None)
    renderMethod: Union[dict, List[dict]] = Field(None)
    proof: Union[dict, List[dict]] = Field(None)

class VerifiableCredential(BaseModel):
    context: List[str] = Field(['https://www.w3.org/ns/credentials/v2'], alias='@context')
    type: List[str] = Field(['VerifiableCredential'])
    id: str = Field()
    issuer: Issuer = Field()
    name: str = Field(None)
    description: str = Field(None)
    credentialSubject: Union[dict, List[dict]] = Field(None)
    credentialStatus: Union[dict, List[dict]] = Field(None)
    credentialSchema: Union[dict, List[dict]] = Field(None)
    termsOfUse: Union[dict, List[dict]] = Field(None)
    renderMethod: Union[dict, List[dict]] = Field(None)
    proof: Union[dict, List[dict]] = Field(None)