from flask import Blueprint
from ..controllers.auth_controller import AuthController
from flask_jwt_extended import jwt_required
from ..helper.decorators import access_control

auth_bp = Blueprint("auth", __name__)
auth_controller = AuthController()

@auth_bp.route("/signup", methods=["POST"])
def signup():
    return auth_controller.customer_signup()

@auth_bp.route("/admin-signup", methods=["POST"])
def admin_signup():
    return auth_controller.admin_signup()

@auth_bp.route("/owner-signup", methods=["POST"])
def owner_signup():
    return auth_controller.owner_signup()

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp_route():
    return auth_controller.verify_otp()

@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    return auth_controller.request_otp()

@auth_bp.route("/signin", methods=["POST"])
def signin():
    return auth_controller.signin()

@auth_bp.route("/signout", methods=["POST"])
def signout():
    return auth_controller.sign_out()


# @auth_bp.route("/update-password", methods=["PATCH"])
# @jwt_required()
# def update_password():
#     return auth_controller.update()

@auth_bp.route("/delete-admin/<string:id>", methods=["PATCH"])
# @jwt_required()
# @access_control("owner")
def delete_admin(id):
    return auth_controller.delete(id)

