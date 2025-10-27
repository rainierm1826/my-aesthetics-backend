from flask import Blueprint
from ..controllers.user_controller import UserController
from flask_jwt_extended import jwt_required
from ..helper.decorators import access_control

user_bp = Blueprint("user_routes", __name__)
user_controller = UserController()

@user_bp.route("", methods=["GET"])
@jwt_required()
def get_user():
    return user_controller.get_by_id()

@user_bp.route("", methods=["PATCH"])
@jwt_required()
def update_user():
    return user_controller.update()

@user_bp.route("/all-customers", methods=["GET"])
@jwt_required()
@access_control("admin", "owner", "customer")
def get_all_customers():
    return user_controller.get_all_customers()
