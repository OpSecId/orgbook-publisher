from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema
from .proof import DataIntegrityProof
from config import settings
import uuid

BASE_CONTEXT = 'https://www.w3.org/ns/credentials/v2'
BASE_VC_TYPE = 'VerifiableCredential'
EXAMPLE_ID = f'https://{settings.DOMAIN}/credentials/{uuid.uuid4()}'
EXAMPLE_ISSUER = 'did:web:example.com:issuer'
EXAMPLE_SUBJECT = {'id': 'did:web:example.com:subject'}

class BaseModel(BaseModel):
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)

class Issuer(BaseModel):
    id: str = Field(example=EXAMPLE_ISSUER)
    name: SkipJsonSchema[str] = Field(None)
    description: SkipJsonSchema[str] = Field(None)

class Credential(BaseModel):
    context: List[str] = Field(None, alias='@context')
    type: List[str] = Field(None)
    id: SkipJsonSchema[str] = Field(None)
    issuer: Issuer = Field(None)
    name: SkipJsonSchema[str] = Field(None)
    description: SkipJsonSchema[str] = Field(None)
    validFrom: SkipJsonSchema[str] = Field(None)
    validUntil: SkipJsonSchema[str] = Field(None)
    credentialSubject: Union[dict, List[dict]] = Field(example=EXAMPLE_SUBJECT)
    credentialStatus: SkipJsonSchema[Union[dict, List[dict]]] = Field(None)
    credentialSchema: SkipJsonSchema[Union[dict, List[dict]]] = Field(None)
    termsOfUse: SkipJsonSchema[Union[dict, List[dict]]] = Field(None)
    renderMethod: SkipJsonSchema[Union[dict, List[dict]]] = Field(None)
    # proof: Union[DataIntegrityProof, List[DataIntegrityProof]] = Field(None)