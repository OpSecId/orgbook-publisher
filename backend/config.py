from pydantic_settings import BaseSettings
import os
import logging
from logging import Logger
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Settings(BaseSettings):
    PROJECT_TITLE: str = "Orgbook Publisher"
    PROJECT_VERSION: str = "v0"

    LOG_LEVEL: int = logging.INFO
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
    LOGGER: Logger = logging.getLogger(__name__)
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

    DOMAIN: str = os.getenv("DOMAIN") or "localhost"

    TRACTION_API_URL: str = os.getenv("TRACTION_API_URL")
    TRACTION_API_KEY: str = os.getenv("TRACTION_API_KEY") or "api_key"
    TRACTION_TENANT_ID: str = os.getenv("TRACTION_TENANT_ID")

    ORGBOOK_URL: str = os.getenv("ORGBOOK_URL")
    ORGBOOK_API_URL: str = f"{ORGBOOK_URL}/api/v4"
    ORGBOOK_VC_SERVICE: str = f"{ORGBOOK_URL}/api/vc"

    TDW_SERVER_URL: str = os.getenv("TDW_SERVER_URL")
    PUBLISHER_MULTIKEY: str = os.getenv("TDW_ENDORSER_MULTIKEY")

    ISSUER_REGISTRY_URL: str = os.getenv("ISSUER_REGISTRY_URL")

    SECRET_KEY: str = TRACTION_API_KEY
    JWT_SECRET: str = TRACTION_API_KEY
    JWT_ALGORITHM: str = "HS256"

    ASKAR_DB: str = os.getenv("POSTGRES_URI") or "sqlite://app.db"
    MONGO_DB: str = os.getenv("MONGODB_URI") or "mongodb://localhost:27017/"


settings = Settings()
