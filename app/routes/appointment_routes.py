from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers.appointment_controller import AppointmentController
from ..helper.decorators import access_control


appointment_bp = Blueprint("appointment", __name__)
appointment_controller = AppointmentController()

@appointment_bp.route("", methods=["POST"])
# @jwt_required()
# @access_control("admin", "owner")
def create_appointment():
    return appointment_controller.create()

@appointment_bp.route("/all", methods=["GET"])
# @access_control("admin", "owner")
def get_appointments():
    return appointment_controller.get_all()

@appointment_bp.route("", methods=["GET"])
# @jwt_required()
def get_appointment():
    return appointment_controller.get_all()

@appointment_bp.route("", methods=["PATCH"])
# @jwt_required()
# @access_control("admin", "owner")
def update_appointment():
    return appointment_controller.update()

@appointment_bp.route("", methods=["PATCH"])
# @jwt_required()
# @access_control("admin", "owner")
def delete_appointment():
    return appointment_controller.delete()
