from flask import Blueprint
from ..controllers.service_controller import ServiceController
from flask_jwt_extended import jwt_required
from ..helper.decorators import access_control


service_bp = Blueprint("service", __name__)
service_controller = ServiceController()

@service_bp.route(rule="", methods=["POST"])
@jwt_required()
@access_control("owner", "admin")
def create_service():
    return service_controller.create()

@service_bp.route(rule="", methods=["GET"])
def get_services():
    return service_controller.get_all()

@service_bp.route(rule="", methods=["DELETE"])
@jwt_required()
@access_control("owner", "admin")
def delete_service():
    return service_controller.delete()


@service_bp.route(rule="", methods=["PATCH"])
@jwt_required()
@access_control("owner", "admin")
def update_service():
    return service_controller.update()
