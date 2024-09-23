from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Settings(BaseSettings):
    PROJECT_TITLE: str = "orgbook-publisher"
    PROJECT_VERSION: str = "v0"
    
    DOMAIN: str = os.environ["DOMAIN"]
    
    TRACTION_API_URL: str = os.environ["TRACTION_API_URL"]
    TRACTION_API_KEY: str = os.environ["TRACTION_API_KEY"]
    TRACTION_TENANT_ID: str = os.environ["TRACTION_TENANT_ID"]
    
    ORGBOOK_URL: str = os.environ["ORGBOOK_URL"]
    ORGBOOK_API_URL: str = f'{ORGBOOK_URL}/api/v4'
    ORGBOOK_VC_SERVICE: str = f'{ORGBOOK_URL}/api/entities'
    
    IPS_DB: str = os.environ["IPS_DB"]
    IPS_HOST: str = os.environ["IPS_HOST"]
    IPS_PORT: str = os.environ["IPS_PORT"]
    IPS_USER: str = os.environ["IPS_USER"]
    IPS_PASS: str = os.environ["IPS_PASS"]
    IPS_SVC: str = os.environ["IPS_SVC"]
    
    TDW_SERVER_URL: str = os.environ["TDW_SERVER_URL"]
    TDW_ENDORSER_DID: str = os.environ["TDW_ENDORSER_DID"]
    
    
    AGENT_ADMIN_URL: str = os.environ["AGENT_ADMIN_URL"]
    AGENT_ADMIN_API_KEY: str = TRACTION_API_KEY
    
    SECRET_KEY: str = TRACTION_API_KEY
    
    ASKAR_DB: str = (
        os.environ["POSTGRES_URI"] if "POSTGRES_URI" in os.environ else "sqlite://app.db"
    )

settings = Settings()
