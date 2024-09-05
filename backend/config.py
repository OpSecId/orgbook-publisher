from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Settings(BaseSettings):
    PROJECT_TITLE: str = "orgbook-publisher"
    PROJECT_VERSION: str = "v0"

    DOMAIN: str = os.environ["DOMAIN"]
    
    ENDORSER_DID: str = os.environ["ENDORSER_DID"]
    ENDORSER_VM: str = f'{ENDORSER_DID}#key-01'
    ENDORSER_MULTIKEY: str = os.environ["ENDORSER_MULTIKEY"]
    
    TRACTION_API_URL: str = os.environ["TRACTION_API_URL"]
    TRACTION_API_KEY: str = os.environ["TRACTION_API_KEY"]
    TRACTION_TENANT_ID: str = os.environ["TRACTION_TENANT_ID"]
    
    ORGBOOK_URL: str = os.environ["ORGBOOK_URL"]
    ORGBOOK_API_URL: str = os.environ["ORGBOOK_API_URL"]
    ARIES_VCR_VC_SERVICE: str = os.environ["ARIES_VCR_VC_SERVICE"]
    
    DID_WEB_SERVER_URL: str = os.environ["DID_WEB_SERVER_URL"]
    
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    
    AGENT_ADMIN_URL: str = os.environ["AGENT_ADMIN_URL"]
    AGENT_ADMIN_API_KEY: str = os.environ["AGENT_ADMIN_API_KEY"]
    
    ASKAR_DB: str = (
        os.environ["POSTGRES_URI"] if "POSTGRES_URI" in os.environ else "sqlite://app.db"
    )

settings = Settings()
