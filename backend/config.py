from pydantic_settings import BaseSettings
import os
import uuid
import secrets
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Settings(BaseSettings):
    PROJECT_TITLE: str = "orgbook-publisher"
    PROJECT_VERSION: str = "v0"

    DOMAIN: str = os.environ["DOMAIN"]
    ENDORSER_DID: str = os.environ["ENDORSER_DID"]
    ENDORSER_VM: str = f'{ENDORSER_DID}#key-01'
    
    ORGBOOK_URL: str = os.environ["ORGBOOK_URL"]
    ORGBOOK_API_URL: str = os.environ["ORGBOOK_API_URL"]
    ORGBOOK_MICROSERVICE_URL: str = os.environ["ORGBOOK_MICROSERVICE_URL"]
    
    DID_WEB_SERVER_URL: str = os.environ["DID_WEB_SERVER_URL"]
    AGENT_ADMIN_URL: str = os.environ["AGENT_ADMIN_URL"]
    AGENT_ADMIN_API_KEY: str = os.environ["AGENT_ADMIN_API_KEY"]
    
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    ENDORSER_MULTIKEY: str = os.environ["ENDORSER_MULTIKEY"]
    ASKAR_DB: str = (
        os.environ["POSTGRES_URI"] if "POSTGRES_URI" in os.environ else "sqlite://app.db"
    )


settings = Settings()
