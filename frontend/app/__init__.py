from flask import Flask, jsonify, render_template, request, url_for
from flask_cors import CORS
from flask_qrcode import QRcode
from config import Config
from datetime import datetime
from app.errors import bp as errors_bp
from app.routes.main import bp as main_bp
from app.routes.auth import bp as auth_bp
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    QRcode(app)
    # Session(app)

    # app.register_blueprint(errors_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app