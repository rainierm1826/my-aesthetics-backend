import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    # Debug mode
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    # Accept JWT tokens from both cookies AND headers for compatibility
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    # Secure should be True in production with HTTPS, False for local development
    JWT_COOKIE_SECURE = os.getenv("ENVIRONMENT", "development") == "production"
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    # SameSite: use "None" when frontend and backend are on different domains (Render)
    # Keep "Lax" for same-site setups. Controlled via ENV var with default "Lax".
    JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "None")
    # Optional cookie domain to scope JWT cookies
    JWT_COOKIE_DOMAIN = os.getenv("JWT_COOKIE_DOMAIN")
    # Token expiration times - 7 days for both access and refresh tokens
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)