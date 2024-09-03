import os

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ["SECRET_KEY"]
    ENDORSER_DID = os.environ["ENDORSER_DID"]
    ENDORSER_SEED = os.environ["ENDORSER_SEED"]
    TRUST_SERVER_URL = os.environ["TRUST_SERVER_URL"]
    AGENT_ADMIN_URL = os.environ["AGENT_ADMIN_URL"]
    AGENT_ADMIN_API_KEY = os.environ["AGENT_ADMIN_API_KEY"]
    POSTGRES_URI = os.environ["POSTGRES_URI"]


class Development(Config):
    DEBUG = True


class Production(Config):
    DEBUG = False
