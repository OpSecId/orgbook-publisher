from quart import Blueprint
from quart_schema import QuartSchema, validate_request, validate_response
from .models import RequestTokenRequest, RequestTokenResponse

bp = Blueprint("auth", __name__)


@bp.route("/token", methods=["POST"])
@validate_request(RequestTokenRequest)
@validate_response(RequestTokenResponse)
def request_token(data: RequestTokenRequest) -> RequestTokenResponse:
    return RequestTokenResponse(access_token="")
