from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .did_document import DidDocument
from config import settings 

class BaseModel(BaseModel):
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)

class Ressources(BaseModel):
    context: str = Field()
    # ocaBundle: str = Field(example='https://')
    # jsonSchema: str = Field(example='https://')
    vocabulary: str = Field(None)
    governance: str = Field(None)

class CredentialRegistration(BaseModel):
    type: str = Field()
    untpType: str = Field(None)
    name: str = Field()
    version: str = Field()
    description: str = Field()
    issuer: str = Field()
    mappings: Dict[str, str] = Field(None)
    ressources: Ressources = Field()