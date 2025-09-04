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
from ..models.voucher_model import Voucher
from ..helper.functions import validate_required_fields
from sqlalchemy import func, asc, desc
from datetime import date
from flask import request

class AppointmentController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Appointment,
            id_field="appointment_id",
            filterable_fields={"status": "status", "branch": (Branch, "branch_id"), "aesthetician": (Aesthetician, "aesthetician_name"), "service": (Service, "service_name")},
            updatable_fields=["status", "aesthetician_rating", "service_rating", "branch_rating", "service_comment", "branch_comment", "aesthetician_comment", "payment_status"],
            joins=[(User, User.user_id==Appointment.user_id, "left"), (WalkIn, WalkIn.walk_in_id==Appointment.walk_in_id, "left"), (Branch, Branch.branch_id==Appointment.branch_id), (Aesthetician, Aesthetician.aesthetician_id==Appointment.aesthetician_id), (Service, Service.service_id==Appointment.service_id)]
        )
    
    
    # def _apply_filters(self, query):
    #     query = super()._apply_filters(query)

    #     identity = get_jwt_identity()
    #     user = User.query.filter_by(account_id=identity).first()
    #     if not user:
    #         raise Exception("User not found")
    #     return query.filter(Appointment.user_id == user.user_id)
    
    

    def _custom_update(self, data):
    # Fetch the appointment being updated
        appointment = Appointment.query.get(data["appointment_id"])
        
        # Use aesthetician_id from data if available, otherwise from appointment
        aesthetician_id = data.get("aesthetician_id") or appointment.aesthetician_id
        aesthetician = Aesthetician.query.get(aesthetician_id)

        if data.get("status") == "completed":
            data["payment_status"] = "completed"
            data["status"] = "completed"
            if aesthetician:
                aesthetician.availability = "available"

        if data.get("branch_rate"):
            self._update_average_rating(Branch, Branch.branch_id, appointment.branch_id, appointment.branch_rating)

        if data.get("service_rate"):
            self._update_average_rating(Service, Service.service_id, appointment.service_id, appointment.service_rating)

        if data.get("aesthetician_rate"):
            self._update_average_rating(Aesthetician, Aesthetician.aesthetician_id, appointment.aesthetician_id, appointment.aesthetician_rating)
        
        
        db.session.commit()
        return appointment

         
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
        required_fields = ["first_name", "last_name", "middle_initial", "sex", "final_payment_method"]
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
        
        service = Service.query.get(appointment_data["service_id"])
        aesthetician = Aesthetician.query.get(appointment_data["aesthetician_id"])
        
        if not service or not aesthetician:
            return jsonify({"status": False, "message": "service or aesthetician not found"}), 404
        
        if aesthetician.availability != "available":
            return jsonify({"status": False, "message": "aesthetician is not available"}), 503
        
        if aesthetician.branch_id != appointment_data['branch_id']:
            return jsonify({"status": False, "message": "aesthetician is not available in this branch"}), 503
        
        if service.branch_id != appointment_data['branch_id']:
            return jsonify({"status": False, "message": "service is not available in this branch"}), 503
        
        # Calculate original amount (base service price)
        original_amount = service.price
        
        # Calculate final amount with all discounts
        final_amount = service.price
        
        # Add pro experience fee
        if aesthetician.experience == "pro":
            final_amount += 1500
        
        # Apply voucher discount if voucher exists
        if "voucher_code" in appointment_data and appointment_data["voucher_code"]:
            voucher = Voucher.query.filter_by(voucher_code=appointment_data["voucher_code"]).first()
            if not voucher:
                return jsonify({"status": False, "message": "voucher does not exist"}), 404
            final_amount -= voucher.discount_amount
            voucher.quantity -= 1

        
        # max final amount is 0. cant be negative
        final_amount = max(0, final_amount)
        
    
        if is_walk_in:
            
            final_amount=appointment_data["to_pay"]
            down_payment_method = None
            down_payment = 0 
            to_pay = final_amount
            payment_status = "partial"

        else:
            down_payment_method = "xendit"
            down_payment = final_amount * 0.2
            to_pay = final_amount - down_payment
            payment_status = "pending"
            
        # Set down payment method 
        appointment_data["down_payment_method"] = down_payment_method
        
        # Set appointment status
        appointment_data["status"] = "waiting"
        appointment_data["payment_status"] = payment_status
        
        
        # Set the status of aesthetician
        aesthetician.availability = "working"
        
        # Set the slot number. This resets after a day
        next_slot = db.session.query(func.count(Appointment.appointment_id)).filter(Appointment.branch_id == appointment_data['branch_id'], Appointment.status == "waiting", func.date(Appointment.created_at) == date.today()).scalar() + 1
        appointment_data['slot_number'] = next_slot
        
        # Set the calculated amounts
        appointment_data["original_amount"] = original_amount
        appointment_data["to_pay"] = to_pay
        appointment_data["down_payment"] = down_payment
        
        
        new_appointment = Appointment(**appointment_data)
        db.session.add(new_appointment)
        return new_appointment
    
    def _update_average_rating(self, model, model_id_field, appointment_fk_field, rating_field):
        ids = db.session.query(model_id_field).distinct().all()
        
        for (id_val,) in ids:
            avg_rating = db.session.query(func.avg(rating_field)).filter(
                appointment_fk_field == id_val,
                rating_field != None
            ).scalar()

            db.session.query(model).filter(model_id_field == id_val).update(
                {"avarage_rate": avg_rating or 0}
            )

        db.session.commit()


                

    
    
    
    
        