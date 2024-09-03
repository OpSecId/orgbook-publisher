from quart import Blueprint
from quart_schema import validate_request, validate_response
from .models import FetchIssuerResponse, RegisterIssuerRequest, RegisterIssuerResponse
from app.plugins import Askar, TrustedWebClient
import secrets
import hashlib
from datetime import datetime

bp = Blueprint("issuers", __name__)


@bp.route("", methods=["GET"])
@validate_response(FetchIssuerResponse)
async def fetch_issuers() -> FetchIssuerResponse:
    return FetchIssuerResponse(
        issuers=[
            await Askar().fetch("issuer", issuer)
            for issuer in await Askar().get_keys("issuer")
        ]
    )


@bp.route("", methods=["POST"])
@validate_request(RegisterIssuerRequest)
@validate_response(RegisterIssuerResponse)
async def register_issuer(data: RegisterIssuerRequest) -> RegisterIssuerResponse:
    did_doc = TrustedWebClient().register_identifier(data.identifier)

    issuer = {
        "id": did_doc["id"],
        "name": data.name,
        "created": str(datetime.now().isoformat("T", "seconds")),
    }
    # await Askar().store("issuer", issuer["id"], issuer)

    client_id = issuer["id"]
    client_secret = secrets.token_urlsafe(32)
    client_hash = hashlib.sha256(client_secret.encode()).hexdigest()
    # await Askar().store("hash", client_id, client_hash)

    return RegisterIssuerResponse(client_id=client_id, client_secret=client_secret)
