from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.controllers.appointment_controller import AppointmentController
from ..helper.decorators import access_control
from app import db
from ..models.appointment_model import Appointment
from datetime import date

webhook_bp = Blueprint("webhook", __name__)
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
@access_control("admin", "owner")
def update_appointment():
    return appointment_controller.update()

@appointment_bp.route("/<string:id>", methods=["PATCH"])
# @jwt_required()
# @access_control("admin", "owner")
def delete_appointment(id):
    return appointment_controller.delete(id)



@webhook_bp.route("/webhook/xendit", methods=["POST"])
def get_xendit_webhook():
    return appointment_controller.xendit_webhook()
