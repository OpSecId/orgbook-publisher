from quart import Blueprint, current_app, abort
from quart_schema import validate_request, validate_response
from .models import RegisterClientRequest, RegisterClientResponse
from app.plugins import Agent
import requests
import secrets

bp = Blueprint("admin", __name__)


@bp.route("/provision", methods=["GET"])
def provision_endorser():
    Agent().provision()
    return {'status': 'ok'}


# @bp.route("/clients", methods=["POST"])
# @validate_request(RegisterClientRequest)
# @validate_response(RegisterClientResponse)
# def register_client(data: RegisterClientRequest) -> RegisterClientResponse:
#     identifier = data.identifier
#     r = requests.get(f'{current_app.config["DID_WEB_SERVER"]}/{identifier}')
#     try:
#         client_id = r.json()["didDocument"]["id"]
#     except:
#         abort(400, "Identifier not available.")
#     client_secret = secrets.token_urlsafe(32)
#     return RegisterClientResponse(client_id=client_id, client_secret=client_secret)
