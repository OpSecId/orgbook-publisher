from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime

class BaseModel(BaseModel):
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)

class IssuanceOptions(BaseModel):
    credentialType: str = Field()

class ProofOptions(BaseModel):
    type: SkipJsonSchema[str] = Field('DataIntegrityProof')
    cryptosuite: SkipJsonSchema[str] = Field('eddsa-jcs-2022')
    proofPurpose: SkipJsonSchema[str] = Field('assertionMethod')
    created: SkipJsonSchema[str] = Field(None)
    verificationMethod: SkipJsonSchema[str] = Field(None)