from flask import Blueprint
from ..controllers.admin_controller import AdminController
from flask_jwt_extended import jwt_required

admin_bp = Blueprint("admin", __name__)
admin_controller = AdminController()


@admin_bp.route("/all", methods=["GET"])
def get_all_admin():
    return admin_controller.get_all()

@admin_bp.route("/", methods=["GET"])
@jwt_required()
def get_admin():
    return admin_controller.get_by_id()

@admin_bp.route("/", methods=["PATCH"])
@jwt_required()
def update_admin():
    return admin_controller.update()