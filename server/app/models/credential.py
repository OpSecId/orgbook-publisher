from dataclasses import dataclass
from typing import List, Union, Dict


@dataclass
class Proof:
    type: str
    id: str
    cryptosuite: str
    verificationMethod: str
    proofPurpose: str
    created: str
    expires: str


@dataclass
class Issuer:
    type: str
    id: str
    name: str
    description: str


@dataclass
class CredentialSubject:
    type: str
    id: str
    name: str
    description: str


@dataclass
class CredentialStatus:
    type: str
    id: str
    statusPurpose: str
    statusListIndex: str
    statusListCredential: str


@dataclass
class CredentialSchema:
    type: str
    id: str


@dataclass
class RenderMethod:
    type: str
    id: str


@dataclass
class TermsOfUse:
    type: str
    id: str
    name: str
    description: str


@dataclass
class Credential:
    context: List[Union[str, Dict[str, str]]]
    type: List[str]
    id: str
    issuer: Issuer
    name: str
    description: str
    credentialSubject: Union[CredentialSubject, List[CredentialSubject]]
    credentialStatus: Union[CredentialStatus, List[CredentialStatus]]
    credentialSchema: Union[CredentialSchema, List[CredentialSchema]]
    renderMethod: Union[RenderMethod, List[RenderMethod]]
    termsOfUse: Union[TermsOfUse, List[TermsOfUse]]
    proof: Union[Proof, List[Proof]]
