from .base_crud_controller import BaseCRUDController
from ..models.admin_model import Admin
from ..models.branch_model import Branch
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

class AdminController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Admin,
            id_field="admin_id",
            required_fields=["email", "password","admin_name", "branch_id", "image"],
            updatable_fields=["admin_name", "branch_id", "image"],
            searchable_fields=["admin_name"],
            filterable_fields={"branch": (Branch, "branch_name")},
            joins=[(Branch, Branch.branch_id==Admin.branch_id)]
        )
    
    def get_by_id(self):
        identity = get_jwt_identity()
        admin = Admin.query.filter_by(account_id=identity).first()
        
        if not admin:
            return jsonify({"status": False, "message": "admin not found"}), 404
        return super().get_by_id(admin.admin_id)
    
    def _custom_update(self, data):
        identity = get_jwt_identity()
        admin = Admin.query.filter_by(account_id=identity).first()
        
        if not admin:
            return jsonify({"status": False, "message": "admin not found"}), 404
        
        data['admin_id'] = admin.admin_id
        return admin