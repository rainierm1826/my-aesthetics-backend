import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
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
    # Allow cookies to be sent with cross-origin requests (important for production)
    # Use Lax instead of None to avoid third-party cookie blocking in browsers
    JWT_COOKIE_SAMESITE = "Lax"
    # Token expiration times - 7 days for both access and refresh tokens
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)