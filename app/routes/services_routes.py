from flask import Blueprint
from ..controllers.service_controller import ServiceController
from flask_jwt_extended import jwt_required
from ..helper.decorators import access_control


service_bp = Blueprint("service", __name__)
service_controller = ServiceController()

@service_bp.route(rule="", methods=["POST"])
# @jwt_required()
# @access_control("owner", "admin")
def create_service():
    return service_controller.create()

@service_bp.route(rule="", methods=["GET"])
def get_services():
    return service_controller.get_all()

@service_bp.route(rule="/<string:service_id>", methods=["GET"])
def get_service(service_id):
    return service_controller.get_by_id(service_id)

@service_bp.route(rule="", methods=["PATCH"])
# @jwt_required()
# @access_control("owner", "admin")
def delete_service():
    return service_controller.delete()


@service_bp.route(rule="", methods=["PATCH"])
# @jwt_required()
# @access_control("owner", "admin")
def update_service():
    return service_controller.update()


@service_bp.route(rule="/service-name", methods=["GET"])
def get_service_name():
    return service_controller.get_service_name()