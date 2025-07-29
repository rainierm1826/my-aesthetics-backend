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

class AppointmentController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Appointment,
            id_field="appointment_id",
            filterable_fields={"status": "status", "branch": (Branch, "branch_name"), "aesthetician": (Aesthetician, "aesthetician_name"), "service": (Service, "service_name")},
            updatable_fields=["status"],
            joins=[(User, User.user_id==Appointment.user_id, "left"), (WalkIn, WalkIn.walk_in_id==Appointment.walk_in_id, "left"), (Branch, Branch.branch_id==Appointment.branch_id), (Aesthetician, Aesthetician.aesthetician_id==Appointment.aesthetician_id), (Service, Service.service_id==Appointment.service_id)]
        )

    def _create_with_relationship(self, data):
        # Walk-in logic
        if data["is_walk_in"] == True:
            required_fields = ["first_name", "last_name", "middle_initial", "phone_number", "sex", "branch_id", "aesthetician_id", "service_id"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing field: {field}")

            new_walk_in = WalkIn(
                first_name=data["first_name"],
                last_name=data["last_name"],
                middle_initial=data["middle_initial"],
                phone_number=data["phone_number"],
                sex=data["sex"],
            )
            db.session.add(new_walk_in)
            db.session.flush()

            new_appointment = Appointment(
                walk_in_id=new_walk_in.walk_in_id,
                user_id=None,
                branch_id=data["branch_id"],
                aesthetician_id=data["aesthetician_id"],
                service_id=data["service_id"],
                status="waiting",
            )
            db.session.add(new_appointment)
            db.session.commit()
            return new_appointment

        # Authenticated user logic
        else:
            identity = get_jwt_identity()
            user = User.query.filter_by(account_id=identity).first()
            if not user:
                return jsonify({"status": False, "message": "user not found"}), 404

            pending_appointment = Appointment.query.filter(Appointment.user_id==user.user_id, Appointment.status == "pending").first()
            if pending_appointment:
                return jsonify({"status": False, "message": "appointment already exists"}), 400

            waiting_appointment = Appointment.query.filter(Appointment.user_id==user.user_id, Appointment.status == "waiting").first()
            if waiting_appointment:
                return jsonify({"status": False, "message": "you are in waiting list"}), 400
            
            new_appointment = Appointment(
                user_id=user.user_id,
                walk_in_id=None,
                branch_id=data["branch_id"],
                aesthetician_id=data["aesthetician_id"],
                service_id=data["service_id"],
                status="waiting",
            )
            db.session.add(new_appointment)
            db.session.commit()
            return new_appointment
        


                

    
    
    
    
        