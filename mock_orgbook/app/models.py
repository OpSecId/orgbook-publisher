from typing import Union, List, Dict
from pydantic import BaseModel, Field

class Credential(BaseModel):
    context: List[str] = Field(['https://www.w3.org/ns/credentials/v2'], alias='@context')
    type: List[str] = Field(['VerifiableCredential'])
    id: str = Field()
    issuer: dict = Field()
    name: str = Field(None)
    description: str = Field(None)
    credentialSubject: Union[dict, List[dict]] = Field(None)
    credentialStatus: Union[dict, List[dict]] = Field(None)
    credentialSchema: Union[dict, List[dict]] = Field(None)
    termsOfUse: Union[dict, List[dict]] = Field(None)
    renderMethod: Union[dict, List[dict]] = Field(None)
    proof: Union[dict, List[dict]] = Field(None)

class Presentation(BaseModel):
    context: List[str] = Field(['https://www.w3.org/ns/credentials/v2'], alias='@context')
    type: List[str] = Field(['VerifiablePresentation'])
    verifiableCredential: List[Credential] = Field(None)
    proof: Union[dict, List[dict]] = Field(None)

class Options(BaseModel):
    credentialId: str = Field()
    credentialType: str = Field()
    credentialVersion: str = Field()

class PublishCredential(BaseModel):
    verifiablePresentation: Presentation = Field()
    options: Options = Field()