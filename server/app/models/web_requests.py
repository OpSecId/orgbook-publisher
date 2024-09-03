from dataclasses import dataclass
from typing import List, Union, Dict


@dataclass
class RequestTokenRequest:
    client_id: str
    client_secret: str


@dataclass
class RequestTokenResponse:
    access_token: str


@dataclass
class CredentialTypeRequest:
    credentialType: dict
    options: dict


@dataclass
class CredentialTypeResponse:
    created: str


@dataclass
class IssueCredentialRequest:
    credential: dict
    options: dict


@dataclass
class IssueCredentialResponse:
    verifiableCredential: dict
