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

    DOMAIN: str = os.environ["DOMAIN"]

    TRACTION_API_URL: str = os.environ["TRACTION_API_URL"]
    TRACTION_API_KEY: str = os.environ["TRACTION_API_KEY"]
    TRACTION_TENANT_ID: str = os.environ["TRACTION_TENANT_ID"]

    ORGBOOK_URL: str = os.environ["ORGBOOK_URL"]
    ORGBOOK_API_URL: str = f"{ORGBOOK_URL}/api/v4"
    ORGBOOK_VC_SERVICE: str = f"{ORGBOOK_URL}/api/vc"

    TDW_SERVER_URL: str = os.environ["TDW_SERVER_URL"]
    TDW_ENDORSER_MULTIKEY: str = os.environ["TDW_ENDORSER_MULTIKEY"]

    ISSUER_REGISTRY_URL: str = os.environ["ISSUER_REGISTRY_URL"]

    # AGENT_ADMIN_URL: str = os.environ["AGENT_ADMIN_URL"]
    # AGENT_ADMIN_API_KEY: str = TRACTION_API_KEY

    # SECRET_KEY: str = TRACTION_API_KEY

    ASKAR_DB: str = (
        os.environ["POSTGRES_URI"]
        if "POSTGRES_URI" in os.environ
        else "sqlite://app.db"
    )

    # ISSUERS: list = [
    #     {
    #         "id": f"did:web:{DOMAIN}:petroleum-and-natural-gas-act:director-of-petroleum-lands",
    #         "name": "Director of Petroleum Lands",
    #         "description": "An officer or employee of the ministry who is designated as the Director of Petroleum Lands by the minister.",
    #         "url": "https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations/ministries/energy-mines-and-petroleum-resources",
    #     }
    # ]


settings = Settings()
