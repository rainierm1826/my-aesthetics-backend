from .base_crud_controller import BaseCRUDController
from ..models.auth_model import Auth
from ..models.user_model import User
from ..models.admin_model import Admin
from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from ..extension import db

class AuthController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Auth,
            id_field="account_id",
            updatable_fields=["password"],
            required_fields=["email", "password", "role_id", "branch_id", "admin_name", "image"],
        )
        
    def create(self):
        data = request.json      
        auth = Auth.query.filter_by(email=data["email"]).first()  
        if auth:
            return jsonify({"status": False, "message": "email name already exist"}), 409
        return super().create()
    
    # sign up customer and admin account
    def _create_with_relationship(self, data):
        image = data.pop("image", None)
        branch_id = data.pop("branch_id", None)
        admin_name = data.pop("admin_name", None)
        auth = Auth(**data)
        db.session.add(auth)
        db.session.flush()
        if data["role_id"] == "1":
            user = User(account_id=auth.account_id)
            db.session.add(user)
        elif data["role_id"] == "2":
            admin = Admin(account_id=auth.account_id, admin_name=admin_name, image=image, branch_id=branch_id)
            db.session.add(admin)
        db.session.commit()
        return auth
    
    def update_password(self):
        pass

    
    # sign in customer and admin account
    def sign_in(self):
        data = request.json
        auth = Auth.query.filter_by(email=data["email"]).first()
        if not auth:
            return jsonify({"status": False, "message": "wrong email"}), 404
        if not auth.check_password(data["password"]):
            return jsonify({"status": False, "message": "wrong password"}), 404
        access_token = create_access_token(identity=auth.account_id, additional_claims={"email": auth.email, "role":auth.role.role_name})
        refresh_token = create_refresh_token(identity=auth.account_id)
        response = make_response(jsonify({
            "status": True,
            "message": "login successfully",
            "user": auth.to_dict(),
            "access_token":access_token,
            "refresh_token":refresh_token
        }))
        response.set_cookie("access_token", access_token, max_age=60 * 60, httponly=True, secure=False)
        response.set_cookie("refresh_token", refresh_token, max_age=60 * 60 * 24 * 7, httponly=True, secure=False)
        return response
    
    # sign out customer and admin account
    def sign_out(self):
        try:
            response = make_response(jsonify({
            "status": True,
            "message": "logout successfully"
        }))
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        except Exception as e:
            return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

    # get user account
    def get_user(self):
        try:
            identity = get_jwt_identity()
            user = Auth.query.filter_by(account_id=identity).first()
            return jsonify({"status": True, "user": user.to_dict()})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # get admin account
    def get_all_admin_credentials(self):
        try:
            admins = Auth.query.filter_by(role_id="2").all()
            return jsonify({"status": True, "admin": [admin.to_dict() for admin in admins]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # delete admin account only. not applicable for customer account
    def delete(self):
        try:
            data = request.json
            auth = Auth.query.filter_by(account_id=data["account_id"]).first()
            
            if not auth:
                return jsonify({"status": False, "message": "account not found"}), 404
            
            if auth.role_id != "2":
                return jsonify({"status": False, "message": "can only delete admin accounts"}), 403

            admin = Admin.query.filter_by(account_id=data["account_id"]).first()
            if admin:
                db.session.delete(admin)
            
            db.session.delete(auth)
            db.session.commit()
            return jsonify({"status": True, "message": "admin account deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500
            
        