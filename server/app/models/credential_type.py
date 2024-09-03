from dataclasses import dataclass
from typing import List


@dataclass
class Topic:
    type: str
    path: str


@dataclass
class RelatedRessource:
    id: str
    type: str
    digest: str


@dataclass
class CredentialType:
    format: str = "vc_di"
    type: str
    version: str
    name: str
    topic: Topic
    verificationMethods: List[str]
    relatedRessources: List[RelatedRessource]
