from typing import Union, List, Dict, Any, Optional
from pydantic import BaseModel, Field, AliasChoices, field_validator

# from .did_document import DidDocument
# from .credential_registration import CredentialRegistration
from . import Credential, CredentialRegistration, IssuanceOptions
from config import settings
import json
import uuid
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
    "type": "Petroleum&NaturalGasTitle",
    "products": [],
    "facilities": [],
}

example_data = {
    "titleType": "",
    "titleNumber": "",
    "titleHolder": "",
    "originType": "",
    "originNumber": "",
    "caveats": [],
    "tracts": [],
    "wells": [],
}

with open("app/data/PetroleumAndNaturalGasTitle.json") as f:
    EXAMPLE_CREDENTIAL_DATA = json.loads(f.read(), object_pairs_hook=OrderedDict)

# class CredentialToPublish(BaseModel):
#     credentialSubject: dict = Field(example=example_subject)


class PublishingOptions(BaseModel):
    validFrom: str = Field(None, example="2024-01-01T00:00:00Z")
    validUntil: str = Field(None, example="2025-01-01T00:00:00Z")
    entityId: str = Field(example="A0131571")
    credentialType: str = Field(example="BCPetroleumAndNaturalGasTitleCredential")


class CoreData(BaseModel):
    entityId: str = Field(example="A0131571")
    resourceId: str = Field(example="62715")
    validFrom: str = Field(None, example="2024-06-01T00:00:00Z")
    validUntil: str = Field(None, example="2025-06-01T00:00:00Z")


class SubjectData(
    BaseModel,
):
    pass


facility_example = {
    "type": ["Facility", "Well"],
    "name": "PACCAN Well",
    "registeredId": "100010408718W603",
    "idScheme": {
        "id": "https://www.bc-er.ca/files/application-manuals/Oil-and-Gas-Activity-Application-Manual/Supporting-Documents/uniquewellidentifierformat.pdf",
        "name": "Unique Well Identifier Format (UWI)",
    },
}
product_example = {
    "type": ["Product", "Tract"],
    "name": "Natural Gas",
    "description": [],
    "rights": ["Included: "],
    "locations": [],
    "registeredId": "2711",
    "idScheme": {
        "id": "https://www.wcoomd.org/en/topics/nomenclature/overview/what-is-the-harmonized-system.aspx",
        "name": "Harmonized System Codes (HS)",
    },
}


class UntpData(BaseModel):
    assessedProduct: List[dict] = Field(example=[product_example])
    assessedFacility: List[dict] = Field(example=[facility_example])


subject_example = {
    "area": "2046",
    "caveats": [
        "PARCEL LOCATED WITHIN TREATY 8; CONSULTATION MAY BE REQUESTED BY A TREATY 8 FIRST NATION.",
        "MAY BE REQUIRED TO COORDINATE ACCESS WITH OTHER OPERATORS AND USERS.",
        "POTENTIAL FOR ARCHAEOLOGICAL RESOURCES EXISTS; OVERVIEW ASSESSMENT MAY BE REQUIRED.",
        "SEASONAL ACCESS RESTRICTIONS MAY APPLY.",
        "POTENTIAL FOR ARCHAEOLOGICAL RESOURCES EXISTS; ARCHAEOLOGICAL IMPACT ASSESSMENT MAY BE REQUIRED.",
    ],
    "titleType": "NaturalGasLease",
    "titleNumber": "62715",
    "titleHolder": "PACIFIC CANBRIAM ENERGY LIMITED",
    "originType": "DrillingLicence",
    "originNumber": "60646",
}


class PublicationCredential(BaseModel):
    type: str = Field(example="BCPetroleumAndNaturalGasTitleCredential")
    validFrom: str = Field(None, example="2024-11-11T00:00:00Z")
    validUntil: str = Field(None, example="2025-11-11T00:00:00Z")
    credentialSubject: dict = Field(
        example={
            "titleType": "NaturalGasLease",
            "titleNumber": "65338",
            "originType": "DrillingLicense",
            "originNumber": "42566",
        }
    )


class PublicationOptions(BaseModel):
    entityId: str = Field(example="A0131571")
    credentialId: str = Field(str(uuid.uuid4()), example=str(uuid.uuid4()))
    cardinalityId: str = Field(example="65338")
    additionalData: dict = Field(
        None,
        example={
            "wells": [
                {"type": ["Facility", "Well"], "id": "urn:code:uwi:", "name": ""}
            ],
            "tracts": [
                {
                    "type": ["Product", "Tract"],
                    "id": "urn:code:hs:",
                    "name": "",
                    "zones": [],
                    "notes": [],
                    "rights": [],
                }
            ],
        },
    )


class Publication(BaseModel):
    credential: PublicationCredential = Field()
    options: PublicationOptions = Field()


class ForwardingOptions(BaseModel):
    entityId: str = Field()
    resourceId: str = Field()
    credentialId: str = Field()
    credentialType: str = Field()


class ForwardCredential(BaseModel):
    verifiableCredential: Credential = Field()
    options: ForwardingOptions = Field()
