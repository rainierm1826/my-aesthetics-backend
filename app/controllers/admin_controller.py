from .base_crud_controller import BaseCRUDController
from ..models.admin_model import Admin
from ..models.branch_model import Branch
from ..models.auth_model import Auth
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, request
from ..extension import db

class AdminController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Admin,
            id_field="admin_id",
            required_fields=["email", "password","admin_name", "branch_id", "image"],
            updatable_fields=["admin_name", "branch_id", "image", "first_name", "last_name", "middle_initial"],
            searchable_fields=["first_name", "last_name"],
            filterable_fields={"branch": (Branch, "branch_id")},
            joins=[(Branch, Branch.branch_id==Admin.branch_id), (Auth, Auth.account_id==Admin.account_id)]
        )
    
    def get_by_id(self):
        identity = get_jwt_identity()
        admin = Admin.query.filter_by(account_id=identity).first()
        
        if not admin:
            return jsonify({"status": False, "message": "admin not found"}), 404
        return super().get_by_id(admin.admin_id)
    
    # update the information of admin by the owner
    def owner_update_admin(self):
        try:
            data = request.json
            print(data)
            user = Admin.query.filter_by(admin_id=data["admin_id"]).first()
            
            for field in self.updatable_fields:
                if field in data:
                    setattr(user, field, data[field])
                    
            db.session.commit()
            return jsonify({
                "status": True,
                "message": "admin updated successfully",
                "admin": user.to_dict()
            })
        except Exception as e:
            print(str(e))
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error", 
                "error": str(e)
            }), 500
    


