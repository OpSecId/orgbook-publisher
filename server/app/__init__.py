from quart import Quart
from quart_schema import QuartSchema
from app.routers import auth_bp, admin_bp, issuers_bp


def create_app(mode="Development"):
    app = Quart(__name__)
    QuartSchema(app)
    app.config.from_object(f"config.{mode}")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(issuers_bp, url_prefix="/issuers")

    @app.route("/server/status", methods=["GET"])
    async def get_server_status():
        return {"status": "ok"}

    return app
