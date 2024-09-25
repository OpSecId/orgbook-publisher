from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Settings(BaseSettings):
    
    IPS_DB: str = os.environ["IPS_DB"]
    IPS_HOST: str = os.environ["IPS_HOST"]
    IPS_PORT: str = os.environ["IPS_PORT"]
    IPS_USER: str = os.environ["IPS_USER"]
    IPS_PASS: str = os.environ["IPS_PASS"]
    IPS_SVC: str = os.environ["IPS_SVC"]

settings = Settings()