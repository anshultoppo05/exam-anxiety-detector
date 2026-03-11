import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
    APP_API_KEY = os.getenv("APP_API_KEY", "dev-api-key")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    BERT_MODEL = os.getenv("BERT_MODEL", "bert-base-uncased")
    SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")
    MAX_INPUT_LENGTH = 10000
    RATE_LIMIT_DEFAULT = "200/day;60/hour"
    RATE_LIMIT_ANALYZE = "20/minute"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    APP_API_KEY = "test-api-key"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
