from ..controllers.base_crud_controller import BaseCRUDController
from ..models.user_model import User
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

class UserController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=User,
            id_field="user_id",
            updatable_fields=["first_name", "last_name", "middle_initial", "phone_number", "birthday", "image"]
        )
        
    def get_by_id(self):
        identity = get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()
        print(user.user_id)
        if not user:
            return jsonify({"status": False, "message": "user not found"}), 404
                
        # Call the base class method directly
        return super().get_by_id(id=user.user_id)
    
    def _custom_update(self, data):
        identity = get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()
        if not user:
            return jsonify({"status": False, "message": "user not found"}), 404
        
        # Add the user_id to the data so the base controller can find the user
        data['user_id'] = user.user_id
        return user
    
    
    