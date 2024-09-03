from dataclasses import dataclass


@dataclass
class RegisterClientRequest:
    name: str
    identifier: str


@dataclass
class RegisterClientResponse:
    client_id: str
    client_secret: str
