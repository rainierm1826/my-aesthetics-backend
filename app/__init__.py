from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config
import os
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    
    CORS(app, origins=os.getenv("FRONTEND_URL"), supports_credentials=True)

    # from .models.role_model import Role
    # from .models.auth_model import Auth
    # from .models.user_role_model import UserRole
    # from .models.address_model import Address
    # from .models.branch_model import Branch
    # from .models.user_model import User
    # from .models.aesthetician_model import Aesthetician
    # from .models.appointment_model import Appointment
    # from .models.comment_model import Comment
    # from .models.service_model import Service
    
    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    from .routes.branch_routes import branch_bp
    from .routes.services_routes import service_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(branch_bp, url_prefix="/branch")
    app.register_blueprint(service_bp, url_prefix="/service")
    
    return app