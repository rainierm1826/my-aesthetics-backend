from flask import Blueprint, request, jsonify
from ..models.appointment_model import Appointment
from ..models.user_model import User
from ..extension import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..helper.functions import update_aesthetician_average_rating

appointment_bp = Blueprint("appointment", __name__)

@appointment_bp.route(rule="/create-appointment", methods=["POST"])
@jwt_required()
def create_appointment():
    try:
        data = request.json
        identity = get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()
        appointment = Appointment.query.filter(Appointment.user_id==user.user_id, Appointment.status!="completed").first()
        
        if appointment:
            return jsonify({"status":False, "message":"one appointment at a time"}), 409
        
        new_appointment = Appointment(
            user_id=user.user_id,
            branch_id=data["branch_id"],
            aesthetician_id=data["aesthetician_id"],
            service_id=data["service_id"],
            status="waiting",
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        return jsonify({"status":True, "message":"created successfully", "appointment":new_appointment.to_dict()}), 201
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    
@appointment_bp.route(rule="/get-appointments", methods=["GET"])
def get_appointments():
    try:
        appointments = Appointment.query.all()
        return jsonify({"status": True, "appointments":[appointment.to_dict() for appointment in appointments]})
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@appointment_bp.route(rule="/get-appointment", methods=["GET"])
@jwt_required()
def get_appointment():
    try:
        identity=get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()
        
        if not user:
            return jsonify({"status": False, "message": "user not found"}), 404 
        
        appointments = Appointment.query.filter_by(user_id=user.user_id).all()
        
        return jsonify({"status": True, "appointment": [appointment.to_dict() for appointment in appointments]}), 200
        
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@appointment_bp.route(rule="/update-appointment", methods=["PATCH"])
def update_appointment():
    try:
        data = request.json
        appointment = Appointment.query.filter_by(appointment_id=data["appointment_id"]).first()
        
        if not appointment:
            return jsonify({"status": False, "message": "Appointment not found"}), 404
        
        updatable_fields = ["branch_id", "aesthetician_id", "service_id", "status"]
        
        for field in updatable_fields:
            if field in data:
                setattr(appointment, field, data[field])
                
        db.session.commit()
                
        return jsonify({"status": True, "message": "Appointment updated", "appointment":appointment.to_dict()}), 200 
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    
@appointment_bp.route(rule="/delete-appointment", methods=["DELETE"])
def delete_appointment():
    try:
        data = request.json
        
        appointment = Appointment.query.filter_by(appointment_id=data["appointment_id"]).first()
        
        if not appointment:
           return jsonify({"status": False, "message": "Appointment not found"}), 404
       
        db.session.delete(appointment)
        db.session.commit()
        
        return jsonify({"status": True, "message":"deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@appointment_bp.route(rule="/rate-appointment", methods=["PATCH"])
def rate_appointment():
    try:
        data = request.json
        appointment = Appointment.query.filter(Appointment.appointment_id==data["appointment_id"], Appointment.status == "completed").first()
        if not appointment:
           return jsonify({"status": False, "message": "Appointment not found or completed"}), 404
        updatable_fields = ("rating", "comment")
        
        for field in updatable_fields:
            if field in data:
                setattr(appointment, field, data[field])
        db.session.commit()
        update_aesthetician_average_rating(appointment.aesthetician.aesthetician_id)
        return jsonify({"status": True, "message": "rate added", "appointment":appointment.to_dict()}), 200 
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500