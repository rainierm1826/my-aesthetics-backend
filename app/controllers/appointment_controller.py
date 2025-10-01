from ..controllers.base_crud_controller import BaseCRUDController
from ..models.appointment_model import Appointment
from ..models.walk_in_model import WalkIn
from ..models.user_model import User
from ..extension import db
from flask_jwt_extended import get_jwt_identity, get_jwt
from flask import jsonify, request
from ..models.branch_model import Branch
from ..models.aesthetician_model import Aesthetician
from ..models.service_model import Service
from ..models.voucher_model import Voucher
from ..helper.functions import validate_required_fields
from sqlalchemy import func, asc, case
from datetime import date
from xendit.apis import InvoiceApi
from ..helper.constant import payment_methods, customer_notification_preference
import xendit
import time
import os


class AppointmentController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Appointment,
            id_field="appointment_id",
            searchable_fields=["appointment_id", "first_name", "last_name"],
            sortable_fields={"slot":Appointment.slot_number},
            filterable_fields={"status": "status", "branch": (Branch, "branch_id"), "aesthetician": (Aesthetician, "aesthetician_name"), "service": (Service, "service_name"), "date":"created_at"},
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
    
    def _apply_sorting(self, query):
        status_order = case(
            (Appointment.status == "waiting", 1),
            (Appointment.status == "on-process", 2),
            (Appointment.status == "completed", 3),
            (Appointment.status == "pending", 5),
            (Appointment.status == "cancelled", 4),
            else_=5,
        )
        return query.order_by(asc(status_order), asc(Appointment.slot_number))
    
    
    # used by owner or admin
    def _custom_update(self, data):
    # Fetch the appointment being updated
        appointment = Appointment.query.get(data["appointment_id"])
        
        # Use aesthetician_id from data if available, otherwise from appointment
        aesthetician_id = data.get("aesthetician_id") or appointment.aesthetician_id
        aesthetician = Aesthetician.query.get(aesthetician_id)

        if data.get("status") == "completed":
            data["status"] = "completed"
            appointment.payment_status = "completed"
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
            
            if isinstance(new_walk_in, tuple):
                return new_walk_in  
            
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
        required_fields = ["first_name", "last_name", "middle_initial"]
        if not validate_required_fields(data, required_fields):
            return jsonify({"status": False, "message": "missing required fields"}), 400
        
        # Filter data to only include WalkIn model fields
        walk_in_fields = ["first_name", "last_name", "middle_initial", "phone_number"]
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

        # Remove WalkIn-specific fields
        walk_in_fields = ["first_name", "last_name", "middle_initial", "phone_number"]
        appointment_data = {key: value for key, value in data.items() if key not in walk_in_fields}
        
        service = Service.query.get(appointment_data["service_id"])
        aesthetician = Aesthetician.query.get(appointment_data["aesthetician_id"])
        branch = Branch.query.get(appointment_data["branch_id"])

        
        if not service or not aesthetician:
            return jsonify({"status": False, "message": "service or aesthetician not found"}), 404
        
        if aesthetician.availability != "available":
            return jsonify({"status": False, "message": "aesthetician is not available"}), 503
        
        if aesthetician.branch.branch_id != appointment_data['branch_id']:
            return jsonify({"status": False, "message": "aesthetician is not available in this branch"}), 503
        
        if service.branch and service.branch.branch_id is not None and service.branch.branch_id != appointment_data['branch_id']:
            return jsonify({"status": False, "message": "service is not available in this branch"}), 503
        
        to_pay = service.discounted_price or service.price
        
        # Add pro experience fee
        if aesthetician.experience == "pro":
            to_pay += 1500
        
        # Apply voucher discount
        voucher = None
        if "voucher_code" in appointment_data and appointment_data["voucher_code"]:
            voucher = Voucher.query.filter_by(voucher_code=appointment_data["voucher_code"]).first()
            if not voucher:
                return jsonify({"status": False, "message": "voucher does not exist"}), 404
            
            if voucher.discount_type == "fixed":
                to_pay -= voucher.discount_amount
            else:
                to_pay -= (to_pay * (voucher.discount_amount / 100))
            
            voucher.quantity -= 1
            db.session.add(voucher)  # ensure change is tracked
        
        # Final amount can't go below zero
        to_pay = max(0, to_pay)
        
        xendit_invoice_url = None
        xendit_invoice_id = None
        
        if is_walk_in:
            to_pay = appointment_data.get("to_pay", to_pay)
            down_payment_method = None
            down_payment = 0
            to_pay = to_pay
            payment_status = "pending"
            status = "waiting"
        else:
            down_payment = to_pay * 0.2
            remaining_payment = to_pay - down_payment
            claims = get_jwt()
            email = claims.get("email")
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({"status": False, "message": "User not found"}), 404
        
            customer_name = f"{user.first_name} {user.middle_initial or ''} {user.last_name}".strip()
            
            try:
                client = xendit.ApiClient()
                api_instance = InvoiceApi(client)
                
                external_id = f"appointment-{int(time.time())}-{user_id}"
                
                invoice_parameters = {
                    "external_id": external_id,
                    "amount": int(down_payment),
                    "payer_email": email,
                    "description": f"Down payment for {service.service_name} - {branch.branch_name}",
                    "currency": "PHP",
                    "invoice_duration": 3600,
                    "success_redirect_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                    "failure_redirect_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/failed",
                    "customer": {
                        "given_names": customer_name,
                        "mobile_number": user.phone_number,
                        "email": email
                    },
                    "customer_notification_preference": customer_notification_preference,
                    "payment_methods":  payment_methods,
                    "items": [
                        {
                            "name": f"Down payment - {service.service_name}",
                            "quantity": 1,
                            "price": int(down_payment)
                        }
                    ],
                    "metadata": {
                        "user_id": str(user_id),
                        "service_id": str(appointment_data["service_id"]),
                        "aesthetician_id": str(appointment_data["aesthetician_id"]),
                        "branch_id": str(appointment_data["branch_id"]),
                        "payment_type": "down_payment"
                    }
                }
                response = api_instance.create_invoice(create_invoice_request=invoice_parameters)
                xendit_invoice_url=response.invoice_url
                xendit_invoice_id=response.id
            except xendit.XenditSdkException as e:
                return jsonify({
                "status": False, 
                "message": f"Failed to create payment invoice: {str(e)}"
            }), 500
            
                    
            down_payment_method = "xendit"
            to_pay = remaining_payment
            payment_status = "pending"
            status = "pending" 
            
            
        appointment_data.update({
            "down_payment_method": down_payment_method,
            "status": status,
            "payment_status": payment_status,
            "to_pay": to_pay,
            "down_payment": down_payment,
            "xendit_invoice_id": xendit_invoice_id,
            "xendit_external_id": f"appointment-{int(time.time())}-{user_id}" if not is_walk_in else None
        })

        if is_walk_in:
            aesthetician.availability = "working"
        

        # Slot number (reset daily)
        # Get the current max slot for today ignoring cancelled appointments
        max_slot = db.session.query(func.max(Appointment.slot_number)) \
            .filter(
                Appointment.branch_id == appointment_data['branch_id'],
                func.date(Appointment.created_at) == date.today(),
                Appointment.status.in_(["waiting", "on-process"]),  # only these count
                Appointment.isDeleted == False
            ).scalar()

        # Assign next slot
        appointment_data['slot_number'] = (max_slot or 0) + 1

        
        # Snapshots
        if is_walk_in:
            customer_name = f"{data.get('first_name', '')} {data.get('middle_initial', '')} {data.get('last_name', '')}".strip()
            appointment_data["customer_name_snapshot"] = customer_name
            appointment_data["phone_number"] = data.get("phone_number")
        elif user_id:
            user = User.query.get(user_id)
            if user:
                appointment_data["customer_name_snapshot"] = customer_name
                appointment_data["phone_number"] = user.phone_number

        if getattr(aesthetician, "experience") == "pro":
            isPro=True
        else:
            isPro=False
        
        aesthetician_name = f"{aesthetician.first_name or ''} {aesthetician.middle_initial or ''} {aesthetician.last_name or ''}".strip()
        
        appointment_data.update({
            "aesthetician_name_snapshot":aesthetician_name,
            "service_name_snapshot": service.service_name,
            "category_snapshot": service.category,
            "price_snapshot": service.price,
            "is_sale_snapshot": getattr(service, "is_sale", False),
            "is_pro_snapshot": isPro,
            "discount_type_snapshot": getattr(service, "discount_type", None),
            "discount_snapshot": getattr(voucher, "discount_amount", None),
            "discounted_price_snapshot": getattr(service, "discounted_price", service.price),
            "branch_name_snapshot": branch.branch_name,
            "voucher_code_snapshot": appointment_data.get("voucher_code", None),
            "voucher_discount_type_snapshot": voucher.discount_type if voucher else None,
            "voucher_discount_amount_snapshot": voucher.discount_amount if voucher else 0.0
        })

        
        new_appointment = Appointment(**appointment_data)
        db.session.add(new_appointment)
        
        # At the end of the function, replace the return statements with:

        if not is_walk_in and xendit_invoice_url:
            new_appointment.payment_url = xendit_invoice_url
            new_appointment.payment_required = True
            
            db.session.commit() 
            db.session.refresh(new_appointment)  
            
            return jsonify({
                "status": True,
                "message": "Appointment created successfully",
                "appointment": new_appointment.to_dict(), 
                "invoice_url": xendit_invoice_url,
            }), 201

        # For walk-in appointments
        db.session.commit()
        db.session.refresh(new_appointment)

        return jsonify({
            "status": True,
            "message": "Walk-in appointment created successfully",
            "appointment": new_appointment.to_dict(),
        }), 201

    # xendit webhooks. use for updating dbs if paid or not
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
