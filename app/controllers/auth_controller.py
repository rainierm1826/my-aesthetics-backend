from .base_crud_controller import BaseCRUDController
from ..models.auth_model import Auth
from ..models.user_model import User
from ..models.admin_model import Admin
from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from ..extension import db
from ..helper.functions import validate_required_fields

class AuthController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Auth,
            id_field="account_id",
            updatable_fields=["password"],
            
        )
        
    def create(self):
        data = request.json      
        auth = Auth.query.filter_by(email=data["email"]).first()  
        if auth:
            return jsonify({"status": False, "message": "email name already exist"}), 409
        return super().create()
    
    # sign up customer and admin account
    def _custom_create(self, data):
        image = data.pop("image", None)
        branch_id = data.pop("branch_id", None)
        first_name = data.pop("first_name", None)
        last_name = data.pop("last_name", None)
        middle_initial = data.pop("middle_initial", None)
        
        # Validate Auth fields
        auth_required_fields = ["email", "password", "role_id"]
        if not validate_required_fields(data, auth_required_fields):
            return jsonify({"status": False, "message": "missing required fields for auth"}), 400
        
        auth = Auth(**data)
        db.session.add(auth)
        db.session.flush()
        
        if data["role_id"] == "1":
            # Create user account
            user = User(account_id=auth.account_id)
            db.session.add(user)
        elif data["role_id"] == "2":
            
            # Create admin account
            admin = Admin(account_id=auth.account_id, first_name=first_name, last_name=last_name, middle_initial=middle_initial, image=image, branch_id=branch_id)
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
        }))
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
            return jsonify({"status": False, "message":"Internal Error"}), 500

    # get user account
    def get_by_id(self):
        identity = get_jwt_identity()
        return super().get_by_id(identity)
    

    # get admin account
    def get_all_admin_credentials(self):
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("limit", 10))
            query = Auth.query.filter_by(role_id="2").order_by(Auth.created_at.desc())
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            items = [admin.to_dict() for admin in pagination.items]
            return jsonify({
                "status": True,
                "message": "Admins retrieved successfully",
                "admin": items,
                "total": pagination.total,
                "pages": pagination.pages,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next
            }), 200

        except Exception as e:      
            return jsonify({"status": False, "message": "Server error", "error": str(e)}), 500

    
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
            
        