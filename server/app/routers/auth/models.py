from dataclasses import dataclass


@dataclass
class RequestTokenRequest:
    client_id: str
    client_secret: str


@dataclass
class RequestTokenResponse:
    access_token: str
