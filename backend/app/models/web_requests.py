from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .did_document import DidDocument
from .credential_registration import CredentialRegistration
from config import settings


class RegisterIssuer(BaseModel):
    identifier: str = Field(example="director-of-petroleum-lands")
    namespace: str = Field(None, example="petroleum-and-natural-gas-act")
    name: str = Field(example="Director of Petroleum Lands")
    description: str = Field(example="An officer or employee of the ministry who is designated as the Director of Petroleum Lands by the minister.")
    
    
class RegisterCredential(BaseModel):
    credentialRegistration: CredentialRegistration = Field()
    
class PublishCredential(BaseModel):
    credentialType: str = Field(example='BCPetroleum&NaturalGasTitle')
    credentialClaims: dict = Field(example={
        "entityId": "A0131571",
        "titleNumber": "745"
    })
