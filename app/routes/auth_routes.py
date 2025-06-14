from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from app.models.auth_model import Auth
from app.models.admin_model import Admin
from app import db
from ..helper.functions import does_exist

auth_bp = Blueprint("auth", __name__)

# create customer
@auth_bp.route(rule="/sign-up", methods=["POST"])
def sign_up():
    try:
        data = request.json
        user = Auth.query.filter_by(email=data["email"]).first()
        if user:
            return jsonify({"status":False, "message":"user already exist"}), 409
        
        
        new_auth = Auth(
            email=data["email"],
            password=Auth.hash_password(data["password"]),
            role_id="1"
        )
        db.session.add(new_auth)
        db.session.commit()
        
        return jsonify({"status":True, "message":"registered successfully", "user":new_user.to_dict()}), 201
        
    except Exception as e:       
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

# create admin
@auth_bp.route(rule="/admin/create-admin", methods=["POST"])
def create_admin():
    try:
        data = request.json
        conflict = does_exist(Auth, "email", data["email"], "email")
        
        if conflict:
            return conflict
                
        with db.session.begin_nested():
            new_auth = Auth(
                email=data["email"],
                password=Auth.hash_password(data["password"]),
                role_id="2"
            )
            db.session.add(new_auth)
            db.session.flush()

            new_admin = Admin(
                account_id=new_auth.account_id,
                branch_id=data["branch_id"],
                admin_name=data["admin_name"],
                image=data["image"]
            )
            db.session.add(new_admin)

        db.session.commit()

        return jsonify({"status":True, "message":"registered successfully", "admin":new_admin.to_dict()}), 201

        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@auth_bp.route(rule="/sign-in", methods=["POST"])
def sign_in():
    try:
        data = request.json
        user = Auth.query.filter_by(email=data["email"]).first()
        
        if not user:
            return jsonify({"status":False, "message":"wrong email"}), 404
        
        if not user.check_password(data["password"]):
            return jsonify({"status":False, "message":"wrong password"}), 404
        
        access_token = create_access_token(identity=user.account_id, additional_claims={"email": user.email, "role":user.role.role_name})
        refresh_token = create_refresh_token(identity=user.account_id)
        response = make_response(jsonify({
            "status": True,
            "message": "login successfully",
            "access_token":access_token,
            "refresh_token":refresh_token
        }))
        
        response.set_cookie("access_token", access_token, max_age=60 * 60, httponly=True, secure=False)
        response.set_cookie("refresh_token", refresh_token, max_age=60 * 60 * 24 * 7, httponly=True, secure=False)
        return response
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500


@auth_bp.route(rule="/sign-out", methods=["POST"])
def sign_out():
    try:
        
        response = make_response({"status":True, "message":"logout successfully"})
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response  
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error"}), 500

    
@auth_bp.route(rule="/get-user", methods=["GET"])
@jwt_required()
def get_user():
    try:
     identity = get_jwt_identity()
     user = Auth.query.filter_by(account_id=identity).first()
     return jsonify({"user": user.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route(rule="/get-users", methods=["GET"])
@jwt_required()
def get_users():
    try:
        users = Auth.query.all()
        return jsonify({"status":True, "message":"get successfully", "users":[user.to_dict() for user in users]}), 200
    
    except Exception as e:
        return jsonify({"status":False, "message": "internal error", "error": str(e)})
