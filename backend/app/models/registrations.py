from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .did_document import DidDocument
from config import settings


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class RelatedResource(BaseModel):
    id: str = Field()
    name: str = Field()


class CredentialRegistration(BaseModel):
    type: str = Field()
    untpType: str = Field(None)
    version: str = Field()
    issuer: str = Field()
    context: str = Field()
    ocaBundle: str = Field()
    relatedResources: dict = Field(None)
