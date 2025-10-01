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
@access_control("admin", "owner")
def get_appointments():
    return appointment_controller.get_all()

# get your appointment
@appointment_bp.route("", methods=["GET"])
@jwt_required()
def get_appointment():
    return appointment_controller.get_all()

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
def xendit_webhook():
    try:
        payload = request.json
        event = payload.get("status")
        invoice_id = payload.get("id")
        appointment = Appointment.query.filter_by(xendit_invoice_id=invoice_id).first()
        if not appointment:
            return jsonify({"status": True, "message": "appointment not found"}), 200  
        
        if event == "PAID":
            appointment.down_payment_status = "completed"
            appointment.status = "waiting" 
            appointment.down_payment_paid_at = date.today()
            appointment.payment_status = "partial"
        elif event == "EXPIRED":
            appointment.down_payment_status = "cancelled"
            appointment.status = "cancelled"
        else:
            appointment.down_payment_status = event.lower()

        appointment.xendit_invoice_id = invoice_id
        db.session.commit()

        return jsonify({"status": True, "message": "webhook processed"}), 200

    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        return jsonify({"status": False, "message": str(e)}), 500

