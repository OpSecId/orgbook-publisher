from typing import Dict, Any
from pydantic import BaseModel, Field


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class IssuerRecord(BaseModel):
    id: str = Field()
    name: str = Field()
    description: str = Field()
    authorized_key: str = Field()
    secret_hash: str = Field()
    did_document: dict = Field()


class CredentialTypeRecord(BaseModel):
    type: str = Field()
    version: str = Field()
    issuer: str = Field()
    json_schema: dict = Field(None)
    context: dict = Field(None)
    core_paths: dict = Field()
    subject_type: str = Field()
    subject_paths: dict = Field()
    additional_type: str = Field(None)
    additional_paths: dict = Field(None)
    credential_template: dict = Field()
    status_lists: list = Field()


class CredentialRecord(BaseModel):
    id: str = Field()
    type: str = Field()
    entity_id: str = Field()
    cardinality_id: str = Field()
    refresh: bool = Field()
    revocation: bool = Field()
    suspension: bool = Field()
    vc: dict = Field()
    jwt: str = Field()


class StatusListRecord(BaseModel):
    id: str = Field()
    indexes: list = Field()
    endpoint: str = Field()
    credential: dict = Field()
