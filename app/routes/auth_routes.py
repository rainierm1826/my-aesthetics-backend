from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from app.models.auth_model import Auth
from app.models.admin_model import Admin
from app.models.user_model import User
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
        
        with db.session.begin_nested():
            new_auth = Auth(
                email=data["email"],
                password=Auth.hash_password(data["password"]),
                role_id="1"
            )
            db.session.add(new_auth)
            db.session.flush()
            
            new_user = User(account_id = new_auth.account_id)
            db.session.add(new_user)
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


# get admins
@auth_bp.route(rule="/admin/get-admins", methods=["GET"])
def get_admin():
    try:
        admins = Admin.query.all()
        return jsonify({"status": True, "message": "get successfully", "services": [admin.to_dict() for admin in admins]}), 200

    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500


# delete admin
@auth_bp.route(rule="/admin/delete-admin", methods=["DELETE"])
def delete_admin():
    try:
        data = request.json
        
        admin = Admin.query.filter_by(admin_id=data["admin_id"]).first()
        
        if not admin:
            return jsonify({"status": False, "message": "Admin not found"}), 404
        
        db.session.delete(admin)
        db.session.commit()
        
        return jsonify({"status": True, "message":"admin deleted"}), 201
    
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500


# update admin
@auth_bp.route(rule="/admin/update-admin", methods=["PATCH"])
def update_admin():
    try:
        data = request.json
        admin = Admin.query.filter_by(admin_id=data["admin_id"]).first()
        if not admin:
            return jsonify({"status": False, "message": "admin not found"}), 404
        
        updatable_fieds = ["admin_name", "branch_id", "password"]
        
        for field in updatable_fieds:
            if field in data:
                setattr(admin, field, data[field])
        db.session.commit()
        
        return jsonify({
            "status": True,
            "message": "Admin updated successfully",
            "admin": admin.to_dict()
        })
        
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
        return jsonify({"status": True, "user": user.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route(rule="/get-users", methods=["GET"])
def get_users():
    try:
        users = Auth.query.all()
        return jsonify({"status":True, "message":"get successfully", "auth":[user.to_dict() for user in users]}), 200
    
    except Exception as e:
        return jsonify({"status":False, "message": "internal error", "error": str(e)})
