from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .did_document import DidDocument
from .credential_registration import CredentialRegistration
from config import settings


class RegisterIssuer(BaseModel):
    name: str = Field(example="Director of Petroleum Lands")
    identifier: str = Field(example="director-of-petroleum-lands")
    namespace: str = Field(None, example="petroleum-and-natural-gas-act")
    description: str = Field(example="An officer or employee of the ministry who is designated as the Director of Petroleum Lands by the minister.")
    url: str = Field(example="https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations/ministries/energy-mines-and-petroleum-resources")
    
    
class RegisterCredential(BaseModel):
    credentialRegistration: CredentialRegistration = Field()
    
class PublishCredential(BaseModel):
    credentialType: str = Field(example='BCPetroleum&NaturalGasTitle')
    credentialClaims: dict = Field(example={
        "registrationNumber": "A0131571",
        "titleNumber": "745"
    })
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)
