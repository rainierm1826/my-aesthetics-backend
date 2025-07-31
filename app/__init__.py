from flask import Flask
from .extension import db, jwt, migrate
from flask_cors import CORS
from .config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    
    CORS(app, origins=os.getenv("FRONTEND_URL"), supports_credentials=True)

    from .models.role_model import Role
    from .models.auth_model import Auth
    from .models.user_role_model import UserRole
    from .models.address_model import Address
    from .models.admin_model import Admin
    from .models.aesthetician_model import Aesthetician
    from .models.branch_model import Branch
    from .models.user_model import User
    from .models.walk_in_model import WalkIn
    from .models.appointment_model import Appointment
    from .models.service_model import Service
    from .models.voucher_model import Voucher
    
    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    from .routes.branch_routes import branch_bp
    from .routes.services_routes import service_bp
    from .routes.user_routes import user_bp
    from .routes.appointment_routes import appointment_bp
    from .routes.aesthetician_routes import aesthetician_bp
    from .routes.analytics_routes import analytics_bp
    
    
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(branch_bp, url_prefix="/branch")
    app.register_blueprint(service_bp, url_prefix="/service")
    app.register_blueprint(aesthetician_bp, url_prefix="/aesthetician")
    app.register_blueprint(appointment_bp, url_prefix="/appointment")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    
    return app