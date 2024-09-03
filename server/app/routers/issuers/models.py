from dataclasses import dataclass
from typing import List


@dataclass
class RegisterIssuerRequest:
    name: str
    identifier: str


@dataclass
class RegisterIssuerResponse:
    client_id: str
    client_secret: str


@dataclass
class Issuer:
    id: str
    name: str
    created: str


@dataclass
class FetchIssuerResponse:
    issuers: List[Issuer]
