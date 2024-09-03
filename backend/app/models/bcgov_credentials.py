from typing import Union, List, Dict
from pydantic import BaseModel, Field, AliasChoices, field_validator

class TractRight(BaseModel):
    product: str = Field(example='NaturalGas')
    inclusive: bool = Field(example=True)
    description: str = Field()

class Tract(BaseModel):
    rights: List[TractRight] = Field()
    locations: List[str] = Field()

class Well(BaseModel):
    name: str = Field()

class TitleHolder(BaseModel):
    id: str = Field()
    name: str = Field()
    identifier: str = Field()
    interest: float = Field()

class Title(BaseModel):
    titleType: str = Field()
    titleNumber: str = Field()
    originType: str = Field()
    originNumber: str = Field()
    caveats: List[str] = Field()
    # wells: List[Well] = Field()
    # tracts: List[Tract] = Field()

class PetroleumAndNaturalGasTitle(BaseModel):
    context: list = Field(alias='@context')
    type: list = Field(['PetroleumAndNaturalGasTitle'])
    validFrom: str = Field()
    validUntil: str = Field()
    # credentialSubject: ConformityAttestation = Field()