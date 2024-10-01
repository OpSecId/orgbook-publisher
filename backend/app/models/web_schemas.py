from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field, AliasChoices, field_validator

# from .did_document import DidDocument
# from .credential_registration import CredentialRegistration
from . import Credential, CredentialRegistration, IssuanceOptions
from config import settings
import json
from collections import OrderedDict


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class RegisterIssuer(BaseModel):
    # namespace: str = Field(example="petroleum-and-natural-gas-act")
    # identifier: str = Field(example="director-of-petroleum-lands")
    name: str = Field(example="Director of Petroleum Lands")
    scope: str = Field(example="Petroleum and Natrual Gas Act")
    description: str = Field(
        example="An officer or employee of the ministry who is designated as the Director of Petroleum Lands by the minister."
    )

    # @field_validator("namespace")
    # @classmethod
    # def validate_namespace(cls, value):
    #     return value

    # @field_validator("identifier")
    # @classmethod
    # def validate_identifer(cls, value):
    #     return value


with open(
    "app/related_resources/credential_types/PetroleumAndNaturalGasTitle.json"
) as f:
    EXAMPLE_CREDENTIAL_TYPE = json.loads(f.read(), object_pairs_hook=OrderedDict)


class RegisterCredential(BaseModel):
    credentialRegistration: CredentialRegistration = Field(
        example=EXAMPLE_CREDENTIAL_TYPE
    )


with open("app/related_resources/credentials/PetroleumAndNaturalGasTitle.json") as f:
    EXAMPLE_CREDENTIAL = json.loads(f.read(), object_pairs_hook=OrderedDict)

EXAMPLE_ISSUANCE_OPTIONS = {"credentialType": "BCPetroleumAndNaturalGasTitleCredential"}


class IssueCredential(BaseModel):
    credential: Credential = Field(example=EXAMPLE_CREDENTIAL)
    options: IssuanceOptions = Field(example=EXAMPLE_ISSUANCE_OPTIONS)


class PublishCredential(BaseModel):
    validFrom: str = Field(None)
    validUntil: str = Field(None)
    credentialType: str = Field(example="BCPetroleum&NaturalGasTitle")
    credentialSubject: dict = Field(example={})

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)
