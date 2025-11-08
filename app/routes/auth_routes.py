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

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    return auth_controller.forgot_password()

@auth_bp.route("/verify-otp-forgot-password", methods=["POST"])
def verify_otp_forgot_password():
    return auth_controller.verify_otp_forgot_password()

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    return auth_controller.reset_password()

@auth_bp.route("/send-email-verification-otp", methods=["POST"])
def send_email_verification_otp():
    return auth_controller.send_email_verification_otp()

@auth_bp.route("/verify-email-otp", methods=["POST"])
def verify_email_otp():
    return auth_controller.verify_email_otp()

@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    return auth_controller.change_password()

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)  # Use refresh token instead of access token
def refresh():
    return auth_controller.refresh()

@auth_bp.route("/verify-session", methods=["GET"])
@jwt_required()
def verify_session():
    return auth_controller.verify_session()

@auth_bp.route("/check-cookies", methods=["GET"])
def check_cookies():
    return auth_controller.check_cookies()

@auth_bp.route("/clear-cookies", methods=["POST"])
def clear_cookies():
    return auth_controller.clear_cookies()
