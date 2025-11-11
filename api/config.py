import os

class Config:
    PROPAGATE_EXCEPTIONS = True
    API_TITLE = "System for tracking subscriptions and payment notifications."
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///data.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days