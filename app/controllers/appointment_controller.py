from ..controllers.base_crud_controller import BaseCRUDController
from ..models.appointment_model import Appointment
from ..models.walk_in_model import WalkIn
from ..models.user_model import User
from ..extension import db
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from ..models.branch_model import Branch
from ..models.aesthetician_model import Aesthetician
from ..models.service_model import Service
from ..helper.validator import validate_required_fields

class AppointmentController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Appointment,
            id_field="appointment_id",
            filterable_fields={"status": "status", "branch": (Branch, "branch_name"), "aesthetician": (Aesthetician, "aesthetician_name"), "service": (Service, "service_name")},
            updatable_fields=["status", "aesthetician_rating", "service_rating", "branch_rating"],
            joins=[(User, User.user_id==Appointment.user_id, "left"), (WalkIn, WalkIn.walk_in_id==Appointment.walk_in_id, "left"), (Branch, Branch.branch_id==Appointment.branch_id), (Aesthetician, Aesthetician.aesthetician_id==Appointment.aesthetician_id), (Service, Service.service_id==Appointment.service_id)]
        )

    def _custom_create(self, data):
        # Walk-in logic
        if data["is_walk_in"] == True:
            # create walk-in
            new_walk_in = self._create_walk_in(data)
            # create appointment
            new_appointment = self._create_appointment(data, walk_in_id=new_walk_in.walk_in_id)
            return new_appointment

        # Authenticated user logic
        else:
            identity = get_jwt_identity()
            user = User.query.filter_by(account_id=identity).first()
            # check if user exists
            if not user:
                return jsonify({"status": False, "message": "user not found"}), 404
            # check if appointment already exists
            pending_appointment = Appointment.query.filter(Appointment.user_id==user.user_id, Appointment.status == "pending").first()
            if pending_appointment:
                return jsonify({"status": False, "message": "appointment already exists"}), 400
            # check if user is in waiting list
            waiting_appointment = Appointment.query.filter(Appointment.user_id==user.user_id, Appointment.status == "waiting").first()
            if waiting_appointment:
                return jsonify({"status": False, "message": "you are in waiting list"}), 400
            
            new_appointment = self._create_appointment(data, user_id=user.user_id)
            return new_appointment
    
    def _create_walk_in(self, data):
        required_fields = ["first_name", "last_name", "middle_initial", "phone_number", "sex"]
        if not validate_required_fields(data, required_fields):
            return jsonify({"status": False, "message": "missing required fields"}), 400
        
        # Filter data to only include WalkIn model fields
        walk_in_fields = ["first_name", "last_name", "middle_initial", "phone_number", "sex"]
        walk_in_data = {key: data[key] for key in walk_in_fields if key in data}
        
        new_walk_in = WalkIn(**walk_in_data)
        db.session.add(new_walk_in)
        db.session.flush()
        return new_walk_in

    def _create_appointment(self, data, walk_in_id=None, user_id=None):
        is_walk_in = data.pop("is_walk_in")
        data["walk_in_id"] = walk_in_id
        data["user_id"] = user_id
        data['status'] = "waiting"
        
        # Remove WalkIn-specific fields from data before creating appointment
        walk_in_fields = ["first_name", "last_name", "middle_initial", "phone_number", "sex"]
        appointment_data = {key: value for key, value in data.items() if key not in walk_in_fields}
        
        new_appointment = Appointment(**appointment_data)
        db.session.add(new_appointment)
        db.session.commit()
        return new_appointment
        


                

    
    
    
    
        