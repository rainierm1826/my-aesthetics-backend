from flask import Blueprint
from ..controllers.auth_controller import AuthController
from flask_jwt_extended import jwt_required

auth_bp = Blueprint("auth", __name__)
auth_controller = AuthController()

@auth_bp.route("/signup", methods=["POST"])
def signup():
    return auth_controller.create()

@auth_bp.route("/signin", methods=["POST"])
def signin():
    return auth_controller.sign_in()

@auth_bp.route("/signout", methods=["POST"])
def signout():
    return auth_controller.sign_out()

@auth_bp.route("/", methods=["GET"])
@jwt_required()
def get_by_id():
    return auth_controller.get_by_id()

@auth_bp.route("/all-admin", methods=["GET"])
@jwt_required()
def get_all_admin_credentials():
    return auth_controller.get_all_admin_credentials()

@auth_bp.route("/update-password", methods=["PATCH"])
@jwt_required()
def update_password():
    return auth_controller.update()

@auth_bp.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_admin():
    return auth_controller.delete() # this delete the admin account only

