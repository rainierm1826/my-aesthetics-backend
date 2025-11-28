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
from ..models.appointment_services_model import AppointmentService

class AppointmentController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Appointment,
            id_field="appointment_id",
            searchable_fields=["appointment_id", "customer_name_snapshot"],
            sortable_fields={"start-time": AppointmentService.start_time},
            filterable_fields={
                "status": "status",
                "branch": (Branch, "branch_id"),
                "date": (AppointmentService, "start_time")
            },
            updatable_fields=["status", "branch_rating", "branch_comment", "payment_status"],
            joins=[
                (User, User.user_id == Appointment.user_id, "left"),
                (WalkIn, WalkIn.walk_in_id == Appointment.walk_in_id, "left"),
                (Branch, Branch.branch_id == Appointment.branch_id),
                (AppointmentService, AppointmentService.appointment_id == Appointment.appointment_id, "left")
            ]
        )
    
    def _update_appointment_status(self, appointment_id):
        """
        Calculate and update the overall appointment status based on service statuses.
        
        Status aggregation logic:
        - All cancelled → appointment cancelled
        - All completed → appointment completed
        - Any on-process → appointment on-process
        - Any waiting (and no on-process) → appointment waiting
        - All pending → appointment pending
        - Mixed statuses → appointment waiting
        """
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return
        
        services = AppointmentService.query.filter_by(appointment_id=appointment_id).all()
        if not services:
            return
        
        # Filter out cancelled services for status calculation
        active_services = [service for service in services if service.service_status != "cancelled"]
        
        # If no active services (all cancelled), then appointment is cancelled
        if not active_services:
            new_status = "cancelled"
        else:
            # Calculate status based only on active (non-cancelled) services
            active_statuses = [service.service_status for service in active_services]
            
            if all(status == "completed" for status in active_statuses):
                new_status = "completed"
            elif any(status == "on-process" for status in active_statuses):
                new_status = "on-process"
            elif any(status == "waiting" for status in active_statuses):
                new_status = "waiting"
            elif all(status == "pending" for status in active_statuses):
                new_status = "pending"
            else:
                # Mixed statuses, default to waiting
                new_status = "waiting"
        
        # Update if changed
        if appointment.status != new_status:
            appointment.status = new_status
            db.session.commit()
    
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
            
            # Dynamically use inner join for AppointmentService if date filter is present
            date_value = request.args.get("date")
            query = db.session.query(self.model)
            for join_item in self.joins:
                # If joining AppointmentService and date filter is present, use inner join
                if (
                    len(join_item) >= 2 and
                    join_item[0] == AppointmentService and
                    date_value
                ):
                    model, condition = join_item[:2]
                    query = query.join(model, condition)
                elif len(join_item) == 2:
                    model, condition = join_item
                    query = query.join(model, condition)
                elif len(join_item) == 3:
                    model, condition, join_type = join_item
                    if join_type == "left":
                        query = query.outerjoin(model, condition)
                    else:
                        query = query.join(model, condition)

            
            # Apply date filtering if date parameter is present
            date_value = request.args.get("date")
            if date_value:
                print(f"[DEBUG] Filtering by date: {date_value}")
                query = query.filter(func.date(AppointmentService.start_time) == date_value)
                print(f"[DEBUG] SQL after date filter: {str(query)}")
            
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
            
            # Ensure distinct appointments (avoid duplicates due to join)
            query = query.distinct(Appointment.appointment_id)
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
        # For PostgreSQL DISTINCT ON, the first ORDER BY must match the DISTINCT ON field
        return query.order_by(Appointment.appointment_id, asc(AppointmentService.start_time))
    
    def _apply_filters(self, query):
        """Override to handle date filtering on start_time datetime field"""
        # Check if there's a search query - if so, skip date filtering to search across all dates
        search_query = request.args.get("query")
        
        for param, model_field in self.filterable_fields.items():
            value = request.args.get(param)
            print(f"[DEBUG] Filtering by {param}: {value}")
            if value:
                # Skip date filter when searching to allow searching across all dates
                if param == "date" and search_query:
                    continue
                # Special handling for date filtering on start_time when model_field is a tuple
                elif param == "date" and isinstance(model_field, tuple):
                    model, field = model_field
                    query = query.filter(func.date(getattr(model, field)) == value)
                    print(f"[DEBUG] Applied date filter on {model.__name__}.{field}: {str(query)}")
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

        # Update branch-level review
        if "branch_rating" in data:
            appointment.branch_rating = data["branch_rating"]
        if "branch_comment" in data:
            appointment.branch_comment = data["branch_comment"]

        # Update per-service reviews
        services_data = data.get("services", [])
        for service_review in services_data:
            appt_service = None
            if "service_id" in service_review:
                appt_service = next((s for s in appointment.services if s.service_id == service_review["service_id"]), None)
            if appt_service:
                if "service_rating" in service_review:
                    appt_service.service_rating = service_review["service_rating"]
                if "service_comment" in service_review:
                    appt_service.service_comment = service_review["service_comment"]
                if "aesthetician_rating" in service_review:
                    appt_service.aesthetician_rating = service_review["aesthetician_rating"]
                if "aesthetician_comment" in service_review:
                    appt_service.aesthetician_comment = service_review["aesthetician_comment"]

        db.session.commit()
        return jsonify({"status": True, "message": "appointment updated successfully"}), 200

    # used by owner or admin
    def _custom_update(self, data):
        appointment = Appointment.query.get(data["appointment_id"])
        if not appointment:
            return jsonify({"status": False, "message": "appointment not found"}), 404

        # Check if this is a service-level update
        service_id = data.get("service_id")
        if service_id:
            # Update specific service within the appointment
            appointment_service = AppointmentService.query.filter_by(
                appointment_id=appointment.appointment_id,
                service_id=service_id
            ).first()
            
            if not appointment_service:
                return jsonify({"status": False, "message": "service not found in appointment"}), 404
            
            # Update service status if provided
            if "status" in data:
                appointment_service.service_status = data["status"]
            
            # Update aesthetician if provided
            if "aesthetician_id" in data:
                new_aesthetician_id = data["aesthetician_id"]
                aesthetician = Aesthetician.query.get(new_aesthetician_id)
                if not aesthetician:
                    return jsonify({"status": False, "message": "aesthetician not found"}), 404
                
                appointment_service.aesthetician_id = new_aesthetician_id
                appointment_service.aesthetician_name_snapshot = f"{aesthetician.first_name or ''} {aesthetician.middle_initial or ''} {aesthetician.last_name or ''}".strip()
                appointment_service.is_pro_snapshot = (aesthetician.experience == "pro")
            
            db.session.commit()
            
            # Automatically update overall appointment status based on service statuses
            self._update_appointment_status(appointment.appointment_id)
            
            db.session.refresh(appointment)
            
            # Emit WebSocket event for appointment update
            emit_appointment_updated(appointment.to_dict())
            
            return appointment

        # Original appointment-level update logic
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
                
                # Get services data for validation
                services_data = data.get("services", [])
                if not services_data:
                    return jsonify({"status": False, "message": "At least one service is required"}), 400
                
                # Check for existing appointments for each service (via AppointmentService)
                for service_item in services_data:
                    service_id = service_item.get("service_id")
                    if not service_id:
                        continue
                    # Pending
                    pending_appointment = db.session.query(Appointment).join(
                        AppointmentService, AppointmentService.appointment_id == Appointment.appointment_id
                    ).filter(
                        Appointment.user_id == user.user_id,
                        Appointment.isDeleted == False,
                        Appointment.status == "pending",
                        AppointmentService.service_id == service_id
                    ).first()
                    if pending_appointment:
                        return jsonify({"status": False, "message": "You already have a pending appointment for this service"}), 400
                    # Waiting
                    waiting_appointment = db.session.query(Appointment).join(
                        AppointmentService, AppointmentService.appointment_id == Appointment.appointment_id
                    ).filter(
                        Appointment.user_id == user.user_id,
                        Appointment.isDeleted == False,
                        Appointment.status == "waiting",
                        AppointmentService.service_id == service_id
                    ).first()
                    if waiting_appointment:
                        return jsonify({"status": False, "message": "You are in the waiting list for this service"}), 400
                    # On-process
                    on_process_appointment = db.session.query(Appointment).join(
                        AppointmentService, AppointmentService.appointment_id == Appointment.appointment_id
                    ).filter(
                        Appointment.user_id == user.user_id,
                        Appointment.isDeleted == False,
                        Appointment.status == "on-process",
                        AppointmentService.service_id == service_id
                    ).first()
                    if on_process_appointment:
                        return jsonify({"status": False, "message": "You are in process list for this service"}), 400  
                
                # Prevent overlapping appointments for the user
                # Parse the date from the first service (assume all services are on the same day)
                try:
                    first_service = services_data[0]
                    # Accept date from client (required)
                    date_str = first_service.get("date") or data.get("date")
                    if not date_str:
                        return jsonify({"status": False, "message": "Date is required for appointment."}), 400
                    # Accept both YYYY-MM-DD and YYYY-MM-DDTHH:MM:SSZ
                    try:
                        new_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except Exception:
                        try:
                            new_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                        except Exception:
                            return jsonify({"status": False, "message": "Invalid date format. Use YYYY-MM-DD."}), 400
                    new_start_time = datetime.strptime(first_service.get("start_time"), "%H:%M").time()
                except Exception:
                    return jsonify({"status": False, "message": "Invalid time format"}), 400

                # Get all user appointments on the same date
                user_appointment_services = db.session.query(AppointmentService).join(
                    Appointment, AppointmentService.appointment_id == Appointment.appointment_id
                ).filter(
                    Appointment.user_id==user.user_id,
                    Appointment.isDeleted==False,
                    Appointment.status.in_(["waiting", "on-process", "pending"]),
                    func.date(AppointmentService.start_time) == new_date
                ).all()

                # Check each new service against existing services
                for service_item in services_data:
                    try:
                        # Accept date from client for each service (fallback to main date)
                        date_str = service_item.get("date") or data.get("date")
                        if not date_str:
                            return jsonify({"status": False, "message": "Date is required for each service."}), 400
                        try:
                            service_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except Exception:
                            try:
                                service_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                            except Exception:
                                return jsonify({"status": False, "message": "Invalid date format. Use YYYY-MM-DD."}), 400
                        new_start_time = datetime.strptime(service_item.get("start_time"), "%H:%M").time()
                        new_start_dt = datetime.combine(service_date, new_start_time)
                        # Always get duration from the service, not from user input
                        service_id = service_item.get("service_id")
                        service = Service.query.get(service_id)
                        if not service:
                            return jsonify({"status": False, "message": f"Service {service_id} not found for overlap check."}), 404
                        duration = service.duration or 60
                        new_end_dt = new_start_dt + timedelta(minutes=duration)
                    except Exception:
                        return jsonify({"status": False, "message": "Invalid time format for service"}), 400

                    # Check against all existing appointment services
                    for apt_service in user_appointment_services:
                        apt_start = apt_service.start_time
                        if isinstance(apt_start, str):
                            try:
                                apt_start = datetime.strptime(apt_start, "%Y-%m-%d %H:%M:%S")
                            except Exception:
                                continue
                        if not isinstance(apt_start, datetime):
                            continue
                        if apt_start.tzinfo is not None:
                            apt_start = apt_start.replace(tzinfo=None)
                        
                        apt_duration = apt_service.duration_snapshot or 60
                        try:
                            apt_duration = int(apt_duration)
                        except Exception:
                            apt_duration = 60
                        apt_end = apt_start + timedelta(minutes=apt_duration)
                        
                        # Check for overlap
                        if new_start_dt < apt_end and new_end_dt > apt_start:
                            return jsonify({"status": False, "message": "You already have an overlapping appointment at this date and time"}), 400

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
        data.pop("walk_in_id", None)
        data.pop("is_walk_in", None)

        data["walk_in_id"] = walk_in_id
        data["user_id"] = user_id
        data['status'] = "pending" if not is_walk_in else "waiting"

        # Remove WalkIn-specific fields
        walk_in_fields = ["first_name", "last_name", "middle_initial", "phone_number"]
        appointment_data = {key: value for key, value in data.items() if key not in walk_in_fields}

        # Expecting a list of services in the request
        services_data = appointment_data.pop("services", None)
        if not services_data or not isinstance(services_data, list) or len(services_data) == 0:
            return jsonify({"status": False, "message": "At least one service is required."}), 400

        # Validate required fields for appointment
        required_fields = ["branch_id"]
        for field in required_fields:
            if field not in appointment_data or not appointment_data[field]:
                return jsonify({"status": False, "message": f"Missing required field: {field}"}), 400

        branch = Branch.query.get(appointment_data["branch_id"])
        if not branch:
            return jsonify({"status": False, "message": "Branch not found"}), 404

        # Set branch name snapshot
        appointment_data["branch_name_snapshot"] = branch.branch_name

        # Snapshots: customer name & phone
        if is_walk_in and walk_in_id:
            walk_in = WalkIn.query.get(walk_in_id)
            if walk_in:
                appointment_data["customer_name_snapshot"] = f"{walk_in.first_name or ''} {walk_in.middle_initial or ''} {walk_in.last_name or ''}".strip()
                appointment_data["phone_number"] = walk_in.phone_number
        elif user_id:
            user = User.query.get(user_id)
            if user:
                appointment_data["customer_name_snapshot"] = f"{user.first_name} {user.middle_initial or ''} {user.last_name}".strip()
                appointment_data["phone_number"] = user.phone_number

        # Calculate total to_pay and create AppointmentService instances
        to_pay = 0
        appointment_services = []
        
        # Use date from client for all services (required)
        # Remove 'date' from appointment_data if present, only use for AppointmentService
        if "date" in appointment_data:
            appointment_data.pop("date")
        

        for service_item in services_data:
            # Validate service
            service_id = service_item.get("service_id")
            if not service_id:
                return jsonify({"status": False, "message": "Each service must have a service_id."}), 400

            service = Service.query.get(service_id)
            if not service:
                return jsonify({"status": False, "message": f"Service {service_id} not found."}), 404

            # Validate aesthetician per service
            aesthetician_id = service_item.get("aesthetician_id")
            aesthetician = None
            if aesthetician_id:
                aesthetician = Aesthetician.query.get(aesthetician_id)
                if not aesthetician:
                    return jsonify({"status": False, "message": f"Aesthetician {aesthetician_id} not found."}), 404
                if aesthetician.availability != "available":
                    return jsonify({"status": False, "message": f"Aesthetician {aesthetician_id} is not available."}), 503
                if aesthetician.branch.branch_id != appointment_data['branch_id']:
                    return jsonify({"status": False, "message": f"Aesthetician {aesthetician_id} is not available in this branch."}), 503

            # Parse start_time for this service
            try:
                # Accept date from client for each service (fallback to main date)
                date_str = service_item.get("date") or data.get("date")
                if not date_str:
                    return jsonify({"status": False, "message": "Date is required for each service."}), 400
                try:
                    service_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except Exception:
                    try:
                        service_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                    except Exception:
                        return jsonify({"status": False, "message": "Invalid date format. Use YYYY-MM-DD."}), 400
                service_start_time = datetime.strptime(service_item["start_time"], "%H:%M")
            except ValueError:
                return jsonify({"status": False, "message": "Invalid time format for service. Use HH:MM (24-hour format)"}), 400

            service_datetime = datetime.combine(service_date, service_start_time.time())
            # Always use the service's duration, not from user input
            service_duration = service.duration or 60
            service_end = service_datetime + timedelta(minutes=service_duration)

            # Check branch slot capacity for this service
            # Query AppointmentService directly and join to Appointment
            existing_services = db.session.query(AppointmentService).join(
                Appointment, AppointmentService.appointment_id == Appointment.appointment_id
            ).filter(
                Appointment.branch_id == appointment_data["branch_id"],
                Appointment.status.in_(["waiting", "on-process", "pending"]),
                Appointment.isDeleted == False,
                func.date(AppointmentService.start_time) == service_date
            ).all()

            concurrent_count = 0
            for apt_service in existing_services:
                apt_start = apt_service.start_time
                apt_end = apt_start + timedelta(minutes=apt_service.duration_snapshot)
                if service_datetime < apt_end and service_end > apt_start:
                    concurrent_count += 1

            if concurrent_count >= branch.slot_capacity:
                return jsonify({
                    "status": False,
                    "message": f"This time slot for {service.service_name} is fully booked. Maximum capacity of {branch.slot_capacity} reached."
                }), 409

            # Calculate price (add pro fee if experience is 'pro' or selected aesthetician is pro)
            service_price = service.discounted_price or service.price
            experience_flag = service_item.get("aesthetician_experience")
            is_pro_experience = isinstance(experience_flag, str) and experience_flag.lower() == "pro"
            is_pro_selected = bool(aesthetician and getattr(aesthetician, "experience", "").lower() == "pro")
            if is_pro_experience or is_pro_selected:
                service_price += 1500
            to_pay += service_price

            # Create AppointmentService snapshot
            # Set is_pro_snapshot based on either provided experience or selected aesthetician
            is_pro_snapshot_value = True if (is_pro_experience or is_pro_selected) else False

            appointment_services.append(AppointmentService(
                appointment_id=None,  # to set later
                service_id=service_id,
                aesthetician_id=aesthetician_id,
                service_name_snapshot=service.service_name,
                price_snapshot=service.price,
                is_sale_snapshot=getattr(service, "is_sale", False),
                category_snapshot=service.category,
                discount_type_snapshot=getattr(service, "discount_type", None),
                discount_snapshot=None,
                discounted_price_snapshot=service.discounted_price or service.price,
                aesthetician_name_snapshot=(f"{aesthetician.first_name or ''} {aesthetician.middle_initial or ''} {aesthetician.last_name or ''}".strip() if aesthetician else None),
                is_pro_snapshot=is_pro_snapshot_value,
                duration_snapshot=service_duration,  # Always from service
                start_time=service_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                service_status="pending"  # Set to pending to match frontend status options
            ))

        # Apply voucher
        voucher = None
        if "voucher_code" in appointment_data and appointment_data["voucher_code"]:
            voucher = Voucher.query.filter_by(voucher_code=appointment_data["voucher_code"]).first()
            if not voucher:
                return jsonify({"status": False, "message": "Voucher does not exist"}), 404
            # Additional validation: dates, quantity, min spend, etc.
            discount_amount_applied = 0
            if voucher.discount_type == "fixed":
                discount_amount_applied = float(voucher.discount_amount or 0)
                to_pay -= discount_amount_applied
            else:
                # percentage
                discount_amount_applied = float(voucher.discount_amount or 0)
                to_pay -= (to_pay * (discount_amount_applied / 100))
            to_pay = max(0, to_pay)
            voucher.quantity -= 1
            db.session.add(voucher)

            # Set voucher snapshots on appointment
            appointment_data["voucher_code_snapshot"] = voucher.voucher_code
            appointment_data["voucher_discount_type_snapshot"] = voucher.discount_type
            appointment_data["voucher_discount_amount_snapshot"] = discount_amount_applied

        appointment_data.update({
            "status": "pending" if not is_walk_in else "waiting",
            "to_pay": to_pay,
            "final_payment_method": appointment_data.get("final_payment_method", "cash"),
            "payment_status": "pending",
        })

        new_appointment = Appointment(**appointment_data)
        db.session.add(new_appointment)
        db.session.commit()
        db.session.refresh(new_appointment)

        # Save AppointmentService records
        for appt_service in appointment_services:
            appt_service.appointment_id = new_appointment.appointment_id
            db.session.add(appt_service)
        db.session.commit()

        emit_new_appointment(new_appointment.to_dict())

        return jsonify({
            "status": True,
            "message": "Appointment created successfully",
            "appointment": new_appointment.to_dict(),
        }), 201 
   
   
    def get_reviews(self, service_id=None, aesthetician_id=None, branch_id=None):
        """
        Fetch reviews for services, aestheticians, or branches.
        For service/aesthetician: fetch from AppointmentService; for branch: from Appointment.
        """
        from ..models.appointment_services_model import AppointmentService
        data = []
        if service_id:
            # Service reviews from AppointmentService
            appt_services = AppointmentService.query.filter_by(service_id=service_id).all()
            for s in appt_services:
                if s.service_rating is not None or s.service_comment:
                    customer_name = s.appointment.customer_name_snapshot if s.appointment else None
                    user_id = s.appointment.user_id if s.appointment else None
                    customer_image = None
                    if user_id:
                        user = User.query.get(user_id)
                        if user and getattr(user, "image", None):
                            customer_image = user.image
                    data.append({
                        "service_rating": s.service_rating,
                        "service_comment": s.service_comment,
                        "customer_name": customer_name,
                        "customer_image": customer_image
                    })
        elif aesthetician_id:
            appt_services = AppointmentService.query.filter_by(aesthetician_id=aesthetician_id).all()
            for s in appt_services:
                if s.aesthetician_rating is not None or s.aesthetician_comment:
                    customer_name = s.appointment.customer_name_snapshot if s.appointment else None
                    user_id = s.appointment.user_id if s.appointment else None
                    customer_image = None
                    if user_id:
                        user = User.query.get(user_id)
                        if user and getattr(user, "image", None):
                            customer_image = user.image
                    data.append({
                        "aesthetician_rating": s.aesthetician_rating,
                        "aesthetician_comment": s.aesthetician_comment,
                        "customer_name": customer_name,
                        "customer_image": customer_image
                    })
        elif branch_id:
            appointments = Appointment.query.filter_by(branch_id=branch_id).all()
            for a in appointments:
                if a.branch_rating is not None or a.branch_comment:
                    customer_image = None
                    if a.user_id:
                        user = User.query.get(a.user_id)
                        if user and getattr(user, "image", None):
                            customer_image = user.image
                    data.append({
                        "branch_rating": a.branch_rating,
                        "branch_comment": a.branch_comment,
                        "customer_name": a.customer_name_snapshot,
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
            # Accept JSON body with a list of services (each with branch_id, service_id, date, and optionally aesthetician_id)
        try:
            # Accept JSON body with a list of services (each with branch_id, service_id, date, and optionally aesthetician_id)
            if request.is_json:
                services = request.get_json().get("services", [])
            else:
                # Fallback to single service via query params for backward compatibility
                services = [{
                    "branch_id": request.args.get("branch_id"),
                    "service_id": request.args.get("service_id"),
                    "aesthetician_id": request.args.get("aesthetician_id"),
                    "date": request.args.get("date")
                }]

            results = []
            print(f"service_id: {request.args.get('service_id')}, aesthetician_id: {request.args.get('aesthetician_id')}, date: {request.args.get('date')}, branch_id: {request.args.get('branch_id')}")
            print(f"[DEBUG] Services for slot availability: {services}")
            identity = get_jwt_identity()
            user = None
            if identity:
                user = User.query.filter_by(account_id=identity).first()

            for svc in services:
                branch_id = svc.get("branch_id")
                service_id = svc.get("service_id")
                date_str = svc.get("date")
                aesthetician_id = svc.get("aesthetician_id")

                # Validate required parameters
                if not all([branch_id, service_id, date_str]):
                    results.append({"status": False, "message": "Missing required parameters: branch_id, service_id, date", "service_id": service_id})
                    continue

                # Parse date
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    results.append({"status": False, "message": "Invalid date format. Use YYYY-MM-DD", "service_id": service_id})
                    continue

                # Fetch branch
                branch = Branch.query.get(branch_id)
                if not branch:
                    results.append({"status": False, "message": "Branch not found", "service_id": service_id})
                    continue

                slot_capacity = branch.slot_capacity
                if not slot_capacity or slot_capacity <= 0:
                    results.append({"status": False, "message": "Invalid branch slot capacity", "service_id": service_id})
                    continue

                # Fetch opening and closing times from branch
                opening_time = branch.opening_time if branch.opening_time else datetime.strptime("10:00", "%H:%M").time()
                closing_time = branch.closing_time if branch.closing_time else datetime.strptime("17:00", "%H:%M").time()

                # Fetch service duration
                service = Service.query.get(service_id)
                if not service:
                    results.append({"status": False, "message": "Service not found", "service_id": service_id})
                    continue

                duration = service.duration  # minutes
                if not duration or duration <= 0:
                    results.append({"status": False, "message": "Invalid service duration", "service_id": service_id})
                    continue

                # If aesthetician_id is provided, validate it
                aesthetician = None
                if aesthetician_id:
                    aesthetician = Aesthetician.query.get(aesthetician_id)
                    if not aesthetician:
                        results.append({"status": False, "message": "Aesthetician not found", "service_id": service_id})
                        continue

                # Define working hours based on branch times
                shift_start = datetime.combine(date, opening_time)
                shift_end = datetime.combine(date, closing_time)
                # If closing time is midnight (00:00:00), it means end of day, so add 1 day
                if closing_time.hour == 0 and closing_time.minute == 0 and closing_time.second == 0:
                    shift_end = shift_end + timedelta(days=1)

                # Fetch all active appointments for the branch on the given date
                branch_appointments = db.session.query(Appointment, AppointmentService).join(AppointmentService).filter(
                    Appointment.branch_id == branch_id,
                    Appointment.isDeleted == False,
                    Appointment.status.in_(["waiting", "on-process", "pending"]),
                    func.date(AppointmentService.start_time) == date
                ).all()

                # Fetch all active appointments for the user on the given date (for self-conflict)
                user_appointments = []
                if user:
                    user_appointments = db.session.query(AppointmentService).join(Appointment, AppointmentService.appointment_id == Appointment.appointment_id).filter(
                        Appointment.user_id == user.user_id,
                        Appointment.isDeleted == False,
                        Appointment.status.in_(["waiting", "on-process", "pending"]),
                        func.date(AppointmentService.start_time) == date
                    ).all()
                # If aesthetician is specified, fetch their appointments
                aesthetician_appointments = []
                if aesthetician_id:
                    aesthetician_appointments = db.session.query(AppointmentService).join(Appointment, AppointmentService.appointment_id == Appointment.appointment_id).filter(
                        AppointmentService.aesthetician_id == aesthetician_id,
                        Appointment.isDeleted == False,
                        Appointment.status.in_(["waiting", "on-process", "pending"]),
                        func.date(AppointmentService.start_time) == date
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
                        # Check for self-conflict (user has overlapping appointment at this time)
                        self_conflict = False
                        if user and user_appointments:
                            for apt in user_appointments:
                                apt_start = apt.start_time
                                if isinstance(apt_start, str):
                                    try:
                                        apt_start = datetime.strptime(apt_start, "%Y-%m-%d %H:%M:%S")
                                    except Exception:
                                        continue
                                if not isinstance(apt_start, datetime):
                                    continue
                                if apt_start.tzinfo is not None:
                                    apt_start = apt_start.replace(tzinfo=None)
                                apt_duration = getattr(apt, "duration_snapshot", 60) or 60
                                try:
                                    apt_duration = int(apt_duration)
                                except Exception:
                                    apt_duration = 60
                                apt_end = apt_start + timedelta(minutes=apt_duration)
                                # Check for overlap
                                if current < apt_end and slot_end > apt_start:
                                    self_conflict = True
                                    break
                        if self_conflict:
                            status = "conflict"
                        else:
                            # Check if aesthetician is busy at this time (if aesthetician_id provided)
                            aesthetician_busy = False
                            if aesthetician_id and aesthetician_appointments:
                                for apt in aesthetician_appointments:
                                    if not apt.duration_snapshot or apt.duration_snapshot <= 0:
                                        continue
                                    existing_start = apt.start_time
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
                                    existing_end = existing_start + timedelta(minutes=apt.duration_snapshot)
                                    # Check for overlap
                                    if current < existing_end and slot_end > existing_start:
                                        aesthetician_busy = True
                                        break
                            if aesthetician_busy:
                                status = "booked"
                            else:
                                # Check branch capacity
                                concurrent_count = 0
                                for appointment, appt_service in branch_appointments:
                                    # Use AppointmentService fields for time and duration
                                    if not appt_service.duration_snapshot or appt_service.duration_snapshot <= 0:
                                        continue
                                    existing_start = appt_service.start_time
                                    if isinstance(existing_start, str):
                                        try:
                                            existing_start = datetime.strptime(existing_start, "%Y-%m-%d %H:%M:%S")
                                        except ValueError:
                                            continue
                                    if not isinstance(existing_start, datetime):
                                        continue
                                    if existing_start.tzinfo is not None:
                                        existing_start = existing_start.replace(tzinfo=None)
                                    
                                    # Ensure the appointment is on the correct date
                                    if existing_start.date() != date:
                                        continue
                                    
                                    existing_end = existing_start + timedelta(minutes=appt_service.duration_snapshot)
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
                results.append(response)

            return jsonify({"results": results})

        except Exception as e:
            return jsonify({"status": False, "message": "Internal error", "error": str(e)})


