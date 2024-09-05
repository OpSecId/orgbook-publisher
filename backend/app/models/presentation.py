from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .credential import VerifiableCredential
from .di_proof import DataIntegrityProof

class Presentation(BaseModel):
    context: List[str] = Field(['https://www.w3.org/ns/credentials/v2'], alias='@context')
    type: List[str] = Field(['VerifiablePresentation'])
    verifiableCredential: List[VerifiableCredential] = Field(None)

class VerifiablePresentation(Presentation):
    proof: Union[dict, List[dict]] = Field(None)