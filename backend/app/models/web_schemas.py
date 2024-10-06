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


with open("app/related_resources/credentials/PetroleumAndNaturalGasTitle.json") as f:
    EXAMPLE_CREDENTIAL = json.loads(f.read(), object_pairs_hook=OrderedDict)

EXAMPLE_ISSUANCE_OPTIONS = {"credentialType": "BCPetroleumAndNaturalGasTitleCredential"}


class IssueCredential(BaseModel):
    credential: Credential = Field(example=EXAMPLE_CREDENTIAL)
    options: IssuanceOptions = Field(example=EXAMPLE_ISSUANCE_OPTIONS)


example_subject = {
    'type': 'Petroleum&NaturalGasTitle',
    'products': [],
    'facilities': [],
}

example_data = {
    'titleType': '',
    'titleNumber': '',
    'titleHolder': '',
    'originType': '',
    'originNumber': '',
    'caveats': [],
    'tracts': [],
    'wells': [],
}

with open("app/data/PetroleumAndNaturalGasTitle.json") as f:
    EXAMPLE_CREDENTIAL_DATA = json.loads(f.read(), object_pairs_hook=OrderedDict)

class DataToPublish(BaseModel):
    pass

# class CredentialToPublish(BaseModel):
#     credentialSubject: dict = Field(example=example_subject)

class PublishingOptions(BaseModel):
    validFrom: str = Field(None, example='2024-01-01T00:00:00Z')
    validUntil: str = Field(None, example='2025-01-01T00:00:00Z')
    entityId: str = Field(example='A0131571')
    credentialType: str = Field(example="BCPetroleumAndNaturalGasTitleCredential")

class PublishCredential(BaseModel):
    data: DataToPublish = Field(example=EXAMPLE_CREDENTIAL_DATA)
    # credential: CredentialToPublish = Field()
    options: PublishingOptions = Field()
