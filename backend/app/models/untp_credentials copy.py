from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator
from .credential import Credential

DCC_CONTEXT = ''

class Entity(BaseModel):
    id: str = Field()
    name: str = Field()

class Product(BaseModel):
    id: str = Field()

class Facility(BaseModel):
    id: str = Field()

class Assessment(BaseModel):
    assessedProducts: List[Product] = Field()
    assessedFacilities: List[Facility] = Field()

class ConformityAttestation(BaseModel):
    type: list = Field(['ConformityAttestation'])
    issuedToParty: Party = Field()
    assessments: List[Assessment] = Field()

class DigitalConformityCredential(Credential):
    context: list = Field([DCC_CONTEXT], alias='@context')
    type: list = Field(['DigitalConformityCredential'])
    id: str = Field()
    issuer: dict = Field(None)
    credentialSubject: ConformityAttestation = Field()