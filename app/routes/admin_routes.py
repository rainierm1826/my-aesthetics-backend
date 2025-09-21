from flask import Blueprint
from ..controllers.admin_controller import AdminController
from flask_jwt_extended import jwt_required
from ..helper.decorators import access_control

admin_bp = Blueprint("admin", __name__)
admin_controller = AdminController()


@admin_bp.route("/all", methods=["GET"])
@jwt_required()
@access_control("owner")
def get_all_admin():
    return admin_controller.get_all()


@admin_bp.route("", methods=["PATCH"])
@jwt_required()
@access_control("owner")
def update_admin():
    return admin_controller.owner_update_admin()