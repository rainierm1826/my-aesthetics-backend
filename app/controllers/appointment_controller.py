from ..controllers.base_crud_controller import BaseCRUDController
from ..models.appointment_model import Appointment
from ..models.walk_in_model import WalkIn
from ..models.user_model import User
from ..extension import db
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, request
from ..models.branch_model import Branch
from ..models.aesthetician_model import Aesthetician
from ..models.service_model import Service
from ..models.voucher_model import Voucher
from sqlalchemy import func, asc
from datetime import  datetime, timedelta
import pytz
from ..socket_events import emit_new_appointment, emit_appointment_updated, emit_appointment_deleted


class AppointmentController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Appointment,
            id_field="appointment_id",
            searchable_fields=["appointment_id", "first_name", "last_name"],
            sortable_fields={"start-time":Appointment.start_time},
            filterable_fields={"status": "status", "branch": (Branch, "branch_id"), "aesthetician": (Aesthetician, "aesthetician_name"), "service": (Service, "service_name"), "date":"start_time"},
            updatable_fields=["status", "aesthetician_id", "aesthetician_name_snapshot", "aesthetician_rating", "service_rating", "branch_rating", "service_comment", "branch_comment", "aesthetician_comment", "payment_status"],
            joins=[(User, User.user_id==Appointment.user_id, "left"), (WalkIn, WalkIn.walk_in_id==Appointment.walk_in_id, "left"), (Branch, Branch.branch_id==Appointment.branch_id), (Aesthetician, Aesthetician.aesthetician_id==Appointment.aesthetician_id, "left"), (Service, Service.service_id==Appointment.service_id)]
        )
    
    def delete(self, id):
        """Override delete to emit WebSocket event"""
        response = super().delete(id)
        
        # If deletion was successful, emit WebSocket event
        if response[1] == 200:  # Check status code
            emit_appointment_deleted(id)
        
        return response
    
    def get_appointment_history(self):
        """Get appointment history for the authenticated user with proper date filtering"""
        try:
            # Get the authenticated user
            identity = get_jwt_identity()
            user = User.query.filter_by(account_id=identity).first()
            if not user:
                return jsonify({"status": False, "message": "User not found"}), 404
            
            # Start with base query with joins
            query = self._apply_joins(db.session.query(self.model))
            
            # Apply date filtering if date parameter is present
            date_value = request.args.get("date")
            if date_value:
                query = query.filter(func.date(Appointment.start_time) == date_value)
            
            # Apply other filters (excluding date since we handled it)
            for param, model_field in self.filterable_fields.items():
                if param == "date":
                    continue  # Skip date, we already handled it
                value = request.args.get(param)
                if value:
                    if isinstance(model_field, tuple):
                        model, field = model_field
                        query = query.filter(getattr(model, field) == value)
                    else:
                        query = query.filter(getattr(self.model, model_field) == value)
            
            # Filter by current user
            query = query.filter(Appointment.user_id == user.user_id)
            
            # Apply soft delete filter
            query = query.filter(self.model.isDeleted == False)
            
            # Apply sorting
            query = self._apply_sorting(query)
            
            # Get all results (no pagination for history)
            appointments = query.all()
            
            return jsonify({
                "status": True,
                "appointment": [appointment.to_dict() for appointment in appointments],
                "total": len(appointments)
            }), 200
        except Exception as e:
            print(f"Error in get_appointment_history: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "Internal error",
                "error": str(e)
            }), 500

    
    def _apply_sorting(self, query):
        return query.order_by(asc(Appointment.start_time))
    
    def _apply_filters(self, query):
        """Override to handle date filtering on start_time datetime field"""
        for param, model_field in self.filterable_fields.items():
            value = request.args.get(param)
            if value:
                # Special handling for date filtering on start_time
                if param == "date" and model_field == "start_time":
                    # Extract date from start_time datetime and compare
                    query = query.filter(func.date(Appointment.start_time) == value)
                elif isinstance(model_field, tuple):
                    model, field = model_field
                    query = query.filter(getattr(model, field) == value)
                else:
                    query = query.filter(getattr(self.model, model_field) == value)
        return query
    
    
    def update_reviews(self):
        data = request.get_json()
        identity = get_jwt_identity()
        
        user = User.query.filter_by(account_id=identity).first()
        if not user:
            return jsonify({"status": False, "message": "user not found"}), 404
        
        appointment = Appointment.query.filter_by(appointment_id=data.get("appointment_id")).first()
        if not appointment:
            return jsonify({"status": False, "message": "appointment not found"}), 404

        if "branch_rating" in data:
            appointment.branch_rating = data["branch_rating"]

        if "service_rating" in data:
            appointment.service_rating = data["service_rating"]

        if "aesthetician_rating" in data:
            appointment.aesthetician_rating = data["aesthetician_rating"]

        comment_fields = ["aesthetician_comment", "branch_comment", "service_comment"]
        for field in comment_fields:
            if field in data:
                setattr(appointment, field, data[field])

        db.session.commit()

        if "branch_rating" in data:
            self._update_average_rating(
                Appointment.branch_rating,
                Appointment.branch_id,
                appointment.branch_id,
                Branch,
                Branch.branch_id
            )

        if "service_rating" in data:
            self._update_average_rating(
                Appointment.service_rating,
                Appointment.service_id,
                appointment.service_id,
                Service,
                Service.service_id
            )

        if "aesthetician_rating" in data:
            self._update_average_rating(
                Appointment.aesthetician_rating,
                Appointment.aesthetician_id,
                appointment.aesthetician_id,
                Aesthetician,
                Aesthetician.aesthetician_id
            )


        return jsonify({"status": True, "message": "appointment updated successfully"}), 200

    # used by owner or admin
    def _custom_update(self, data):
        appointment = Appointment.query.get(data["appointment_id"])
        if not appointment:
            return jsonify({"status": False, "message": "appointment not found"}), 404

        # Save old values to know which branches need recalculation
        old_branch_id = appointment.branch_id
        old_status = appointment.status

        # Apply provided updates to the appointment object (only status handled here explicitly)
        new_status = data.get("status")
        if new_status and new_status != old_status:
            appointment.status = new_status
            # mark when it entered the new status
            appointment.status_updated_at = datetime.utcnow()

            if new_status == "completed":
                appointment.payment_status = "completed"
                # update aesthetician availability if applicable
                aesthetician_id = data.get("aesthetician_id") or appointment.aesthetician_id
                aesthetician = Aesthetician.query.get(aesthetician_id)
                if aesthetician:
                    aesthetician.availability = "available"

        branch_ids_to_recalc = {appointment.branch_id}
        if "branch_id" in data and data["branch_id"] and data["branch_id"] != old_branch_id:
            branch_ids_to_recalc.add(old_branch_id)
            branch_ids_to_recalc.add(data["branch_id"])
            appointment.branch_id = data["branch_id"]

        db.session.commit()
        db.session.refresh(appointment)
        
        # Emit WebSocket event for appointment update
        emit_appointment_updated(appointment.to_dict())
        
        return appointment

    
    def _custom_create(self, data):
        try:
            # Walk-in logic - identified by walk_in_id field
            if "walk_in_id" in data and data["walk_in_id"]:
                walk_in_id = data.get("walk_in_id")
                
                # Validate that walk-in customer exists
                walk_in = WalkIn.query.filter_by(walk_in_id=walk_in_id, isDeleted=False).first()
                if not walk_in:
                    return jsonify({"status": False, "message": "walk-in customer not found"}), 404
                
                # create appointment with existing walk-in customer
                new_appointment = self._create_appointment(data, walk_in_id=walk_in_id, is_walk_in=True)
                return new_appointment

            # Authenticated user logic
            else:
                identity = get_jwt_identity()
                user = User.query.filter_by(account_id=identity).first()
                # check if user exists
                if not user:
                    return jsonify({"status": False, "message": "user not found"}), 404
                # check if appointment already exists
                pending_appointment = Appointment.query.filter(Appointment.user_id==user.user_id, Appointment.status == "pending", Appointment.isDeleted==False).first()
                if pending_appointment:
                    return jsonify({"status": False, "message": "Appointment already exists"}), 400
                # check if user is in waiting list
                waiting_appointment = Appointment.query.filter(Appointment.user_id==user.user_id, Appointment.status == "waiting", Appointment.isDeleted==False).first()
                if waiting_appointment:
                    return jsonify({"status": False, "message": "You are in waiting list"}), 400
                
                on_process_appointment = Appointment.query.filter(Appointment.user_id==user.user_id, Appointment.status == "on-process", Appointment.isDeleted==False).first()
                if on_process_appointment:
                    return jsonify({"status": False, "message": "You are in process list"}), 400  
                
                new_appointment = self._create_appointment(data, user_id=user.user_id, is_walk_in=False)
                return new_appointment
        except Exception as e:
            print(f"Error in _custom_create: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": False,
                "message": f"Error creating appointment: {str(e)}"
            }), 500
    
    def _create_appointment(self, data, walk_in_id=None, user_id=None, is_walk_in=False):
        print(data)
        # Remove walk_in_id and is_walk_in from data if present (we'll use the parameters instead)
        data.pop("walk_in_id", None)
        data.pop("is_walk_in", None)
        
        data["walk_in_id"] = walk_in_id
        data["user_id"] = user_id
        data['status'] = "waiting"

        # Remove WalkIn-specific fields
        walk_in_fields = ["first_name", "last_name", "middle_initial", "phone_number"]
        appointment_data = {key: value for key, value in data.items() if key not in walk_in_fields}
        
        # Validate required fields
        # aesthetician_id is now optional - will be assigned by admin later if not provided
        required_fields = ["service_id", "branch_id", "date", "start_time"]
        for field in required_fields:
            if field not in appointment_data or not appointment_data[field]:
                return jsonify({"status": False, "message": f"Missing required field: {field}"}), 400
        
        service = Service.query.get(appointment_data["service_id"])
        branch = Branch.query.get(appointment_data["branch_id"])

        if not service:
            return jsonify({"status": False, "message": "service not found"}), 404
        
        if not branch:
            return jsonify({"status": False, "message": "branch not found"}), 404
        
        # If aesthetician_id is provided, validate it
        aesthetician = None
        if appointment_data.get("aesthetician_id"):
            aesthetician = Aesthetician.query.get(appointment_data["aesthetician_id"])
            if not aesthetician:
                return jsonify({"status": False, "message": "aesthetician not found"}), 404
            
            if aesthetician.availability != "available":
                return jsonify({"status": False, "message": "aesthetician is not available"}), 503
            
            if aesthetician.branch.branch_id != appointment_data['branch_id']:
                return jsonify({"status": False, "message": "aesthetician is not available in this branch"}), 503
        
        if service.branch and service.branch.branch_id is not None and service.branch.branch_id != appointment_data['branch_id']:
            return jsonify({"status": False, "message": "service is not available in this branch"}), 503
        
        
        # Parse and validate start time
        try:
            print(f"DEBUG - Received start_time: {appointment_data['start_time']}")
            start_time = datetime.strptime(appointment_data["start_time"], "%H:%M")
            print(f"DEBUG - Parsed start_time: {start_time}")
        except ValueError:
            return jsonify({"status": False, "message": "Invalid time format. Use HH:MM (24-hour format)"}), 400
        
        # Validate that start time is within salon working hours (10:00 - 17:00)
        start_hour = start_time.hour
        
        duration = service.duration or 60  # fallback to 60 mins if missing
        
        # Check branch slot capacity for the requested time
        appointment_datetime = datetime.combine(
            datetime.strptime(appointment_data["date"], "%Y-%m-%d").date(),
            start_time.time()
        )
        appointment_end = appointment_datetime + timedelta(minutes=duration)
        
        # Get all appointments for this branch on the same date
        existing_appointments = Appointment.query.filter(
            Appointment.branch_id == appointment_data["branch_id"],
            Appointment.status.in_(["waiting", "on-process", "pending"]),
            Appointment.isDeleted == False,
            func.date(Appointment.start_time) == appointment_datetime.date()
        ).all()
        
        # Count how many appointments overlap with the new time slot
        concurrent_count = 0
        for apt in existing_appointments:
            apt_start = apt.start_time
            if isinstance(apt_start, str):
                try:
                    apt_start = datetime.strptime(apt_start, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
            
            if not isinstance(apt_start, datetime):
                continue
            
            # Remove timezone info if present
            if apt_start.tzinfo is not None:
                apt_start = apt_start.replace(tzinfo=None)
            
            apt_end = apt_start + timedelta(minutes=apt.duration)
            
            # Check if appointments overlap
            if appointment_datetime < apt_end and appointment_end > apt_start:
                concurrent_count += 1
        
        # Check if adding this appointment would exceed capacity
        if concurrent_count >= branch.slot_capacity:
            return jsonify({
                "status": False,
                "message": f"This time slot is fully booked. Maximum capacity of {branch.slot_capacity} reached."
            }), 409
        
        # Only check for overlapping appointments if aesthetician is assigned
        if aesthetician:
            overlapping = Appointment.query.filter(
            Appointment.aesthetician_id == appointment_data["aesthetician_id"],
            Appointment.status.in_(["waiting", "on-process", "pending"]),
            Appointment.isDeleted == False
            ).all()

            # Check overlaps in Python
            for apt in overlapping:
                # Convert apt_start to time if it's a datetime
                apt_start_time = apt.start_time.time() if isinstance(apt.start_time, datetime) else apt.start_time
                apt_end = (datetime.combine(datetime.today(), apt_start_time) + timedelta(minutes=apt.duration)).time()
                
                # Get time from our new appointment
                new_start_time = start_time.time()
                new_end = (start_time + timedelta(minutes=duration)).time()
                
                if apt_start_time < new_end and apt_end > new_start_time:
                    return jsonify({
                        "status": False,
                        "message": "Aesthetician already has an appointment at that time"
                    }), 409

        to_pay = service.discounted_price or service.price
        
        # Add pro experience fee if aesthetician_experience is "pro"
        # This applies regardless of whether aesthetician is assigned yet
        if appointment_data.get("aesthetician_experience") == "pro":
            to_pay += 1500
        # Or check the assigned aesthetician's experience level
        elif aesthetician and aesthetician.experience == "pro":
            to_pay += 1500
        
        # Apply voucher discount
        voucher = None
        if "voucher_code" in appointment_data and appointment_data["voucher_code"]:
            voucher = Voucher.query.filter_by(voucher_code=appointment_data["voucher_code"]).first()
            if not voucher:
                return jsonify({"status": False, "message": "voucher does not exist"}), 404
            
            # Check if voucher is expired (use naive datetime to match database)
            now = datetime.now()
            if now < voucher.valid_from:
                return jsonify({"status": False, "message": "voucher is not yet valid"}), 400
            if now > voucher.valid_until:
                return jsonify({"status": False, "message": "voucher has expired"}), 400
            
            # Check if voucher has quantity left
            if voucher.quantity <= 0:
                return jsonify({"status": False, "message": "voucher is no longer available"}), 400
            
            # Check minimum spend requirement
            if to_pay < voucher.minimum_spend:
                return jsonify({
                    "status": False, 
                    "message": f"Minimum spend of ₱{voucher.minimum_spend} required to use this voucher"
                }), 400
            
            if voucher.discount_type == "fixed":
                to_pay -= voucher.discount_amount
            else:
                to_pay -= (to_pay * (voucher.discount_amount / 100))
            
            voucher.quantity -= 1
            db.session.add(voucher)  # ensure change is tracked
        
        # Final amount can't go below zero
        to_pay = max(0, to_pay)
        
        if is_walk_in:
            to_pay = appointment_data.get("to_pay", to_pay)
            payment_status = "pending"
            status = "waiting"
        else:
            payment_status = "pending"
            status = "pending"
        
        # Debug: Log the date and time before combining
        print(f"DEBUG - appointment_data['date']: {appointment_data['date']}")
        print(f"DEBUG - appointment_data['start_time']: {appointment_data['start_time']}")
        
        final_start_time = datetime.combine(
            datetime.strptime(appointment_data["date"], "%Y-%m-%d").date(),
            datetime.strptime(appointment_data["start_time"], "%H:%M").time()
        ).replace(tzinfo=None)
        print(f"DEBUG - Final start_time to be saved: {final_start_time}")
        print(f"DEBUG - Final start_time date component: {final_start_time.date()}")
        print(f"DEBUG - Final start_time time component: {final_start_time.time()}")
        
        appointment_data.update({
            "status": status,
            "duration": service.duration,
            "start_time": final_start_time,  # Store as naive datetime to avoid timezone conversion issues
            "payment_status": payment_status,
            "to_pay": to_pay,
        })
        
        # Snapshots
        customer_name_snapshot = None
        
        if is_walk_in and walk_in_id:
            walk_in = WalkIn.query.get(walk_in_id)
            if walk_in:
                customer_name_snapshot = f"{walk_in.first_name or ''} {walk_in.middle_initial or ''} {walk_in.last_name or ''}".strip()
                appointment_data["customer_name_snapshot"] = customer_name_snapshot
                appointment_data["phone_number"] = walk_in.phone_number
        elif user_id:
            user = User.query.get(user_id)
            if user:
                customer_name_snapshot = f"{user.first_name} {user.middle_initial or ''} {user.last_name}".strip()
                appointment_data["customer_name_snapshot"] = customer_name_snapshot
                appointment_data["phone_number"] = user.phone_number

        # Create aesthetician snapshots only if aesthetician is assigned
        if aesthetician:
            isPro = getattr(aesthetician, "experience") == "pro"
            aesthetician_name = f"{aesthetician.first_name or ''} {aesthetician.middle_initial or ''} {aesthetician.last_name or ''}".strip()
        else:
            isPro = appointment_data.get("aesthetician_experience") == "pro"
            aesthetician_name = None
        
        appointment_data.update({
            "aesthetician_name_snapshot": aesthetician_name,
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
            "voucher_discount_amount_snapshot": voucher.discount_amount if voucher else 0.0,
            "duration_snapshot": service.duration
        })

        # Remove temporary fields that are not part of the Appointment model
        appointment_data.pop("date", None)
        appointment_data.pop("voucher_code", None)
        appointment_data.pop("aesthetician_experience", None)
        
        new_appointment = Appointment(**appointment_data)
        db.session.add(new_appointment)
        db.session.commit()
        db.session.refresh(new_appointment)

        # Emit WebSocket event for new appointment
        emit_new_appointment(new_appointment.to_dict())

        return jsonify({
            "status": True,
            "message": "Appointment created successfully",
            "appointment": new_appointment.to_dict(),
        }), 201

    def get_reviews(self, service_id=None, aesthetician_id=None, branch_id=None):
        query = Appointment.query.with_entities(
            Appointment.service_rating,
            Appointment.branch_rating,
            Appointment.aesthetician_rating,
            Appointment.service_comment,
            Appointment.branch_comment,
            Appointment.aesthetician_comment,
            Appointment.customer_name_snapshot,
            Appointment.user_id,
        )

        if service_id:
            query = query.filter_by(service_id=service_id)
        elif aesthetician_id:
            query = query.filter_by(aesthetician_id=aesthetician_id)
        elif branch_id:
            query = query.filter_by(branch_id=branch_id)

        reviews = query.all()

        if not reviews:
            return {"status": False, "message": "No reviews found"}, 404

        data = []
        for r in reviews:
            # Skip appointments where all ratings and comments are None/empty
            if (
                r.service_rating is None and
                r.branch_rating is None and
                r.aesthetician_rating is None and
                not r.service_comment and
                not r.branch_comment and
                not r.aesthetician_comment
            ):
                continue

            customer_image = None
            # Registered user
            user = User.query.get(r.user_id)
            if user and getattr(user, "image", None):
                customer_image = user.image


            data.append({
                "service_rating": r.service_rating,
                "branch_rating": r.branch_rating,
                "aesthetician_rating": r.aesthetician_rating,
                "service_comment": r.service_comment,
                "branch_comment": r.branch_comment,
                "aesthetician_comment": r.aesthetician_comment,
                "customer_name": r.customer_name_snapshot,
                "customer_image": customer_image
            })

        if not data:
            return {"status": False, "message": "No reviews found"}, 404

        return {"status": True, "review": data}



    def _update_average_rating(self, appointment_model_field, appointment_fk_field, fk_value, target_model, target_id_field):
        # Compute the average rating for the given foreign key (only non-null ratings)
        avg_rating = db.session.query(func.avg(appointment_model_field)).filter(
            appointment_fk_field == fk_value,
            appointment_model_field.isnot(None)
        ).scalar()

        # Update the corresponding model's average_rate
        db.session.query(target_model).filter(target_id_field == fk_value).update(
            {"average_rate": round(avg_rating, 2) if avg_rating else 0}
        )

        db.session.commit()

    def get_available_slots(self):
        """
        Generate available appointment slots for a given branch and aesthetician.
        
        Query params:
        - branch_id: Required - The branch ID
        - aesthetician_id: Optional - The aesthetician ID (if provided, checks aesthetician availability)
        - service_id: Required - The service ID (to get duration)
        - date: Required - The date in YYYY-MM-DD format
        
        Returns slots with status: "available", "booked", or "past"
        """
        try:
            branch_id = request.args.get("branch_id")
            aesthetician_id = request.args.get("aesthetician_id")
            service_id = request.args.get("service_id")
            date_str = request.args.get("date")

            # Validate required parameters
            if not all([branch_id, service_id, date_str]):
                return jsonify({"status": False, "message": "Missing required parameters: branch_id, service_id, date"})

            # Parse date
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"status": False, "message": "Invalid date format. Use YYYY-MM-DD"})

            # Fetch branch
            branch = Branch.query.get(branch_id)
            if not branch:
                return jsonify({"status": False, "message": "Branch not found"})

            slot_capacity = branch.slot_capacity
            if not slot_capacity or slot_capacity <= 0:
                return jsonify({"status": False, "message": "Invalid branch slot capacity"})

            # Fetch opening and closing times from branch
            opening_time = branch.opening_time if branch.opening_time else datetime.strptime("10:00", "%H:%M").time()
            closing_time = branch.closing_time if branch.closing_time else datetime.strptime("17:00", "%H:%M").time()

            # Fetch service duration
            service = Service.query.get(service_id)
            if not service:
                return jsonify({"status": False, "message": "Service not found"})

            duration = service.duration  # minutes
            if not duration or duration <= 0:
                return jsonify({"status": False, "message": "Invalid service duration"})

            # If aesthetician_id is provided, validate it
            aesthetician = None
            if aesthetician_id:
                aesthetician = Aesthetician.query.get(aesthetician_id)
                if not aesthetician:
                    return jsonify({"status": False, "message": "Aesthetician not found"})

            # Define working hours based on branch times
            shift_start = datetime.combine(date, opening_time)
            shift_end = datetime.combine(date, closing_time)
            
            # If closing time is midnight (00:00:00), it means end of day, so add 1 day
            if closing_time.hour == 0 and closing_time.minute == 0 and closing_time.second == 0:
                shift_end = shift_end + timedelta(days=1)

            # Fetch all active appointments for the branch on the given date
            branch_appointments = Appointment.query.filter(
                Appointment.branch_id == branch_id,
                Appointment.isDeleted == False,
                Appointment.status.in_(["waiting", "on-process", "pending"]),
                func.date(Appointment.start_time) == date
            ).all()

            # If aesthetician is specified, fetch their appointments
            aesthetician_appointments = []
            if aesthetician_id:
                aesthetician_appointments = Appointment.query.filter(
                    Appointment.aesthetician_id == aesthetician_id,
                    Appointment.isDeleted == False,
                    Appointment.status.in_(["waiting", "on-process", "pending"]),
                    func.date(Appointment.start_time) == date
                ).all()

            # Generate slots
            slots = []
            current = shift_start
            
            # Get current time in Philippines timezone
            philippines_tz = pytz.timezone('Asia/Manila')
            now = datetime.now(philippines_tz).replace(tzinfo=None)  # Get PH time as naive datetime

            while current + timedelta(minutes=duration) <= shift_end:
                slot_end = current + timedelta(minutes=duration)
                
                # Default status
                status = "available"
                
                # Check if slot is in the past by comparing the actual datetime
                # This works correctly even when closing time is midnight (next day)
                if current < now:
                    status = "past"
                else:
                    # Check if aesthetician is busy at this time (if aesthetician_id provided)
                    aesthetician_busy = False
                    if aesthetician_id and aesthetician_appointments:
                        for appointment in aesthetician_appointments:
                            if not appointment.duration or appointment.duration <= 0:
                                continue
                            
                            existing_start = appointment.start_time
                            
                            # Handle string conversion
                            if isinstance(existing_start, str):
                                try:
                                    existing_start = datetime.strptime(existing_start, "%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    continue
                            
                            if not isinstance(existing_start, datetime):
                                continue
                            
                            if existing_start.tzinfo is not None:
                                existing_start = existing_start.replace(tzinfo=None)
                            
                            if existing_start.date() != date:
                                existing_start = datetime.combine(date, existing_start.time())
                            
                            existing_end = existing_start + timedelta(minutes=appointment.duration)
                            
                            # Check for overlap
                            if current < existing_end and slot_end > existing_start:
                                aesthetician_busy = True
                                break
                    
                    if aesthetician_busy:
                        status = "booked"
                    else:
                        # Check branch capacity
                        concurrent_count = 0
                        for appointment in branch_appointments:
                            if not appointment.duration or appointment.duration <= 0:
                                continue

                            existing_start = appointment.start_time
                            
                            if isinstance(existing_start, str):
                                try:
                                    existing_start = datetime.strptime(existing_start, "%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    continue

                            if not isinstance(existing_start, datetime):
                                continue

                            if existing_start.tzinfo is not None:
                                existing_start = existing_start.replace(tzinfo=None)

                            if existing_start.date() != date:
                                existing_start = datetime.combine(date, existing_start.time())

                            existing_end = existing_start + timedelta(minutes=appointment.duration)

                            # Check for overlap
                            if current < existing_end and slot_end > existing_start:
                                concurrent_count += 1

                        # If concurrent appointments >= slot_capacity, mark as booked
                        if concurrent_count >= slot_capacity:
                            status = "booked"

                # Add slot with status
                slot_range = {
                    "start_time": current.strftime("%I:%M %p"),
                    "end_time": slot_end.strftime("%I:%M %p"),
                    "start_time_24": current.strftime("%H:%M"),
                    "end_time_24": slot_end.strftime("%H:%M"),
                    "status": status
                }
                slots.append(slot_range)

                # Move to next slot
                current += timedelta(minutes=duration)

            response = {
                "status": True,
                "branch_id": branch_id,
                "service_id": service_id,
                "date": date_str,
                "available_slots": slots,
                "service_duration": duration,
                "slot_capacity": slot_capacity,
                "working_hours": {
                    "opening_time": opening_time.strftime("%H:%M"),
                    "closing_time": closing_time.strftime("%H:%M")
                }
            }

            if aesthetician_id:
                response["aesthetician_id"] = aesthetician_id

            return jsonify(response)

        except Exception as e:
            return jsonify({"status": False, "message": "Internal error", "error": str(e)})


