from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.controllers.appointment_controller import AppointmentController
from ..helper.decorators import access_control
from app import db
from ..models.appointment_model import Appointment
from datetime import date

appointment_bp = Blueprint("appointment", __name__)
appointment_controller = AppointmentController()

@appointment_bp.route("", methods=["POST"])
@jwt_required()
@access_control("admin", "owner", "customer")
def create_appointment():
    return appointment_controller.create()

@appointment_bp.route("/all", methods=["GET"])
@jwt_required()
def get_appointments():
    return appointment_controller.get_all()

# get your own appointment/history
@appointment_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    return appointment_controller.get_appointment_history()

@appointment_bp.route("", methods=["PATCH"])
@jwt_required()
def update_appointment():
    return appointment_controller.update()

@appointment_bp.route("/reviews", methods=["PATCH"])
@jwt_required()
@access_control("customer")
def update_review():
    return appointment_controller.update_reviews()

@appointment_bp.route("/<string:id>", methods=["PATCH"])
# @jwt_required()
# @access_control("admin", "owner")
def delete_appointment(id):
    return appointment_controller.delete(id)

@appointment_bp.route("/reviews", methods=["GET"])
def get_reviews():
    service_id = request.args.get("service_id")
    aesthetician_id = request.args.get("aesthetician_id")
    branch_id = request.args.get("branch_id")

    return appointment_controller.get_reviews(
        service_id=service_id,
        aesthetician_id=aesthetician_id,
        branch_id=branch_id
    )

@appointment_bp.route("/available-slots", methods=["GET"])
def get_available_slots():
    return appointment_controller.get_available_slots()
