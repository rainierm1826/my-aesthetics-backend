from ..controllers.base_crud_controller import BaseCRUDController
from ..models.user_model import User
from ..models.owner_model import Owner
from ..models.admin_model import Admin
from flask_jwt_extended import get_jwt_identity, get_jwt
from flask import jsonify, request
from ..extension import db
from datetime import datetime, timezone


class UserController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=User,
            id_field="user_id",
            updatable_fields=["first_name", "last_name", "middle_initial", "phone_number", "birthday", "image"]
        )

    def get_by_id(self):
        identity = get_jwt_identity()
        role = get_jwt().get("role")

        model_map = {
            "customer": User,
            "admin": Admin, 
            "owner": Owner
        }
        
        model = model_map.get(role)
        if not model:
            return jsonify({"status": False, "message": "Invalid role"}), 400

        try:
            user = model.query.filter(model.account_id == identity).first()
            
            if not user:
                return jsonify({"status": False, "message": "user not found"}), 404
            
            return jsonify({
                "status": True,
                "message": "user retrieved successfully",
                "user": user.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500

    
    def update(self, id=None):
        identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")
        
        # Get the appropriate model and user
        if role == "customer":
            user = User.query.filter_by(account_id=identity).first()
        elif role == "admin":
            user = Admin.query.filter_by(account_id=identity).first()
        elif role == "owner":
            user = Owner.query.filter_by(account_id=identity).first()
        else:
            return jsonify({"status": False, "message": "Invalid role"}), 400
        
        if not user:
            return jsonify({"status": False, "message": "user not found"}), 404
        
        try:
            data = request.get_json()
            
            # Update only the allowed fields
            for field in self.updatable_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({
                "status": True,
                "message": f"{user.__class__.__tablename__} updated successfully",
                user.__class__.__tablename__: user.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error", 
                "error": str(e)
            }), 500
    
    
    