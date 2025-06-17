from flask import Blueprint, jsonify, request
from ..models.user_model import User
from ..extension import db
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt

user_bp = Blueprint("user", __name__)

@user_bp.route(rule="/update-user", methods=["PATCH"])
def update_user():
    try:
        data = request.json
        
        user = User.query.filter_by(user_id=data["user_id"]).first()
        
        if not user:
            return jsonify({"status": False, "message": "user not found"}), 404
        
        updatable_fields = ["first_name", "last_name", "middle_initial", "phone_number", "birthday", "image"]
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
                
        db.session.commit()
        return jsonify({
            "status": True,
            "message": "User updated successfully",
            "user": user.to_dict()
        })
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@user_bp.route(rule="/get-user", methods=["GET"])
@jwt_required()
def get_user():
    try:
        identity = get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()
        if not user:
            return jsonify({
                "status": False,
                "message": "User not found"
            }), 404
        return jsonify({"status": True, "user": user.to_dict()})
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@user_bp.route(rule="/get-users", methods=["GET"])
def get_users():
    try:
        users = User.query.all()
        return jsonify({"status":True, "message":"get successfully", "users":[user.to_dict() for user in users]}), 200
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500