from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .did_documents import DidDocument
from config import settings


class RegisterIdentifier(BaseModel):
    didDocument: DidDocument = Field()
    
    
class CredentialTopic(BaseModel):
    type: str = Field(example='registration.registries.ca')
    sourceId: dict = Field(example={
          "path": "$.credentialSubject.identifier"
        })

class CredentialType(BaseModel):
    type: str = Field(example='BCExampleCredential')
    version: str = Field(example='1.0')
    extraTypes: list = Field(example=[])
    name: str = Field(example='BC Example Credential')
    description: str = Field(example='BC Example Credential of a Buisness Registration.')
    verificationMethod: str = Field(example=settings.ENDORSER_MULTIKEY)
    topic: CredentialTopic = Field(example={
        "type": "registration.registries.ca",
        "sourceId": {
          "path": "$.credentialSubject.issuedTo.identifier"
        }
    })
    context: str = Field(example='https://')
    ocaBundle: str = Field(example='https://')
    jsonSchema: str = Field(example='https://')
    governance: str = Field(example='https://')
    vocabulary: str = Field(example='https://')
    
class PublishCredential(BaseModel):
    registrationId: str = Field(example='')
    credentialType: str = Field(example='BCExampleCredential')
    extraTypes: list = Field(example=[])
    credential: dict = Field(example={})
