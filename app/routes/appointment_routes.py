from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers.appointment_controller import AppointmentController


appointment_bp = Blueprint("appointment", __name__)
appointment_controller = AppointmentController()

@appointment_bp.route("/", methods=["POST"])
@jwt_required()
def create_appointment():
    return appointment_controller.create()

@appointment_bp.route("/all", methods=["GET"])
def get_appointments():
    return appointment_controller.get_all()

@appointment_bp.route("/", methods=["GET"])
@jwt_required()
def get_appointment():
    return appointment_controller.get_all()

@appointment_bp.route("/", methods=["PATCH"])
def update_appointment():
    return appointment_controller.update()

@appointment_bp.route("/", methods=["DELETE"])
def delete_appointment():
    return appointment_controller.delete()
