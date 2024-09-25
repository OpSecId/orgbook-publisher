from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Settings(BaseSettings):
    PROJECT_TITLE: str = "Orgbook Publisher"
    PROJECT_VERSION: str = "v0"
    
    DOMAIN: str = os.environ["DOMAIN"]
    
    # TRACTION_API_URL: str = os.environ["TRACTION_API_URL"]
    # TRACTION_API_KEY: str = os.environ["TRACTION_API_KEY"]
    # TRACTION_TENANT_ID: str = os.environ["TRACTION_TENANT_ID"]
    
    ORGBOOK_URL: str = os.environ["ORGBOOK_URL"]
    ORGBOOK_API_URL: str = f'{ORGBOOK_URL}/api/v4'
    ORGBOOK_VC_SERVICE: str = f'{ORGBOOK_URL}/api/vc'

    TDW_SERVER_URL: str = os.environ["TDW_SERVER_URL"]

    # AGENT_ADMIN_URL: str = os.environ["AGENT_ADMIN_URL"]
    # AGENT_ADMIN_API_KEY: str = TRACTION_API_KEY
    
    # SECRET_KEY: str = TRACTION_API_KEY
    
    ASKAR_DB: str = (
        os.environ["POSTGRES_URI"] if "POSTGRES_URI" in os.environ else "sqlite://app.db"
    )
    
    ISSUERS: list = [
        {
            "id": f"did:web:{DOMAIN}:petroleum-and-natural-gas-act:director-of-petroleum-lands",
            "name": "Director of Petroleum Lands",
            "description": "An officer or employee of the ministry who is designated as the Director of Petroleum Lands by the minister.",
            "url": "https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations/ministries/energy-mines-and-petroleum-resources"
        }
    ]

settings = Settings()
