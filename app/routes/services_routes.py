from flask import Blueprint
from ..controllers.service_controller import ServiceController


service_bp = Blueprint("service", __name__)
service_controller = ServiceController()

@service_bp.route(rule="", methods=["POST"])
def create_service():
    return service_controller.create()

@service_bp.route(rule="", methods=["GET"])
def get_services():
    return service_controller.get_all()

@service_bp.route(rule="", methods=["DELETE"])
def delete_service():
    return service_controller.delete()


@service_bp.route(rule="", methods=["PATCH"])
def update_service():
    return service_controller.update()
