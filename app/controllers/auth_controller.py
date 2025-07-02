from .base_crud_controller import BaseCRUDController
from ..models.auth_model import Auth
from ..models.user_model import User
from flask import request, jsonify

class AuthController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Auth,
            id_field="account_id",
            updatable_fields=["password"],
            valid_fields=["email", "password", "role_id"],
        )
        
    def create(self):
        data = request.json      
        auth = Auth.query.filter_by(email=data["email"]).first()  
        if auth:
            return jsonify({"status": False, "message": "email name already exist"}), 409
        return super().create()
    
    def _create_with_relationship(self, data):
         pass
        