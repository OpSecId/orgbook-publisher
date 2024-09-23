import os, redis, json
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    ENV = os.environ["ENV"] if 'ENV' in os.environ else 'development'
    DEBUG = os.environ["DEBUG"] if 'DEBUG' in os.environ else True
    TESTING = os.environ["TESTING"] if 'TESTING' in os.environ else True
    SECRET_KEY = os.environ["SECRET_KEY"] if 'SECRET_KEY' in os.environ else 's3cret'

    # # Backend API
    # ORGBOOK_PUBLISHER = os.environ["ORGBOOK_PUBLISHER"]

    # # Flask-session with redis
    # SESSION_TYPE = "redis"
    # SESSION_REDIS = redis.from_url(os.environ["REDIS_URL"])
    # SESSION_COOKIE_NAME = "dtt"

    # File upload security
    UPLOAD_EXTENSIONS = [".json", ".jsonld"]
    MAX_CONTENT_LENGTH = 1024 * 1024