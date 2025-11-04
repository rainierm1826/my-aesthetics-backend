from ..controllers.base_crud_controller import BaseCRUDController
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch
from ..models.service_model import Service
from ..models.appointment_model import Appointment
from ..extension import db
from flask import jsonify, request
from datetime import datetime, time, timedelta
from sqlalchemy import func

class AestheticianController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Aesthetician,
            id_field="aesthetician_id",
            required_fields=["first_name", "last_name", "middle_initial", "phone_number", "sex", "experience"],
            updatable_fields=["first_name", "last_name", "middle_initial", "phone_number", "image", "sex", "experience", "branch_id", "availability"],
            searchable_fields=["first_name", "last_name"],
            filterable_fields={"sex": "sex", "experience": "experience", "availability": "availability", "branch": (Branch, "branch_id")},
            sortable_fields={"rate": Aesthetician.average_rate, "name":Aesthetician.first_name},
            joins=[(Branch, Branch.branch_id==Aesthetician.branch_id)]
        )
    
    def get_aesthetician_name(self):
        try:
            
            branch = request.args.get("branch")
            
            query = (
                db.session.query(
                    Aesthetician.aesthetician_id,
                    Aesthetician.first_name,
                    Aesthetician.last_name,
                    Aesthetician.middle_initial,
                    Aesthetician.experience
                ).filter_by(isDeleted=False)
            )
            
            if branch:
                query = query.filter(Aesthetician.branch_id==branch, Aesthetician.availability=="available")
            
            result = query.all()

            aestheticians = [
                {
                    "aesthetician_id": a.aesthetician_id,
                    "first_name": a.first_name,
                    "last_name": a.last_name,
                    "middle_initial": a.middle_initial,
                    "experience":a.experience
                }
                for a in result
            ]

            return jsonify({"status": True, "message": "Retrieved successfully", "aesthetician": aestheticians})
        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)})

    def _custom_create(self, data):
        data["availability"] = "available"
        new_aesthetician = Aesthetician(**data)
        db.session.add(new_aesthetician)
        return new_aesthetician
    
    
    def get_available_slots(self):
        try:
            aesthetician_id = request.args.get("aesthetician_id")
            service_id = request.args.get("service_id")
            date_str = request.args.get("date")  

            if not all([aesthetician_id, service_id, date_str]):
                return jsonify({"status": False, "message": "Missing params"})

            date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Fetch aesthetician to get branch info
            aesthetician = Aesthetician.query.get(aesthetician_id)
            if not aesthetician:
                return jsonify({"status": False, "message": "Aesthetician not found"})

            # Fetch branch to get slot_capacity
            branch = Branch.query.get(aesthetician.branch_id)
            if not branch:
                return jsonify({"status": False, "message": "Branch not found"})

            slot_capacity = branch.slot_capacity
            if not slot_capacity or slot_capacity <= 0:
                return jsonify({"status": False, "message": "Invalid branch slot capacity"})

            # Fetch service duration (in minutes)
            service = Service.query.get(service_id)
            if not service:
                return jsonify({"status": False, "message": "Service not found"})

            duration = service.duration  # minutes
            
            # Validate service duration
            if not duration or duration <= 0:
                return jsonify({"status": False, "message": "Invalid service duration"})

            # Working hours: 10:00 AM to 11:00 PM
            shift_start_hour = 10
            shift_start_minute = 0
            shift_end_hour = 23
            shift_end_minute = 0
            
            shift_start = datetime.combine(date, time(shift_start_hour, shift_start_minute))
            shift_end = datetime.combine(date, time(shift_end_hour, shift_end_minute))

            # Fetch all non-deleted appointments for that aesthetician on the same date
            aesthetician_appointments = Appointment.query.filter(
                Appointment.aesthetician_id == aesthetician_id,
                Appointment.isDeleted == False,
                func.date(Appointment.start_time) == date
            ).all()

            # Fetch all non-deleted and active appointments for the branch on the same date
            # This is used to check branch capacity
            branch_appointments = Appointment.query.filter(
                Appointment.branch_id == aesthetician.branch_id,
                Appointment.isDeleted == False,
                Appointment.status.in_(["waiting", "on-process", "pending"]),
                func.date(Appointment.start_time) == date
            ).all()

            # Build available slot ranges
            # Slots are generated based on service duration intervals
            slots = []
            current = shift_start
            
            # Get current time for checking if slots are in the past
            now = datetime.now()

            while current + timedelta(minutes=duration) <= shift_end:
                slot_end = current + timedelta(minutes=duration)
                
                # Determine slot status
                status = "available"
                
                # Check if slot is in the past
                if current < now:
                    status = "past-time"
                else:
                    # First, check if this specific aesthetician has an appointment at this time
                    aesthetician_busy = False
                    for appointment in aesthetician_appointments:
                        # Skip appointments with invalid duration
                        if not appointment.duration or appointment.duration <= 0:
                            continue
                        
                        # Get appointment start time - handle both datetime objects and strings
                        existing_start = appointment.start_time
                        
                        # If it's a string, parse it to datetime
                        if isinstance(existing_start, str):
                            try:
                                # Try parsing with datetime format
                                existing_start = datetime.strptime(existing_start, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                # If parsing fails, skip this appointment
                                continue
                        
                        # Ensure it's a datetime object and is timezone-naive
                        if not isinstance(existing_start, datetime):
                            continue
                        
                        if existing_start.tzinfo is not None:
                            existing_start = existing_start.replace(tzinfo=None)
                        
                        # Ensure appointment start time is on the correct date
                        if existing_start.date() != date:
                            existing_start = datetime.combine(date, existing_start.time())
                        
                        # Calculate appointment end time
                        existing_end = existing_start + timedelta(minutes=appointment.duration)
                        
                        # Check for overlap
                        if current < existing_end and slot_end > existing_start:
                            aesthetician_busy = True
                            break
                    
                    if aesthetician_busy:
                        status = "not-available"
                    else:
                        # Second, check if branch capacity is reached
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

                        # If concurrent appointments >= slot_capacity, mark as not-available
                        if concurrent_count >= slot_capacity:
                            status = "not-available"

                # Add slot with status
                slot_range = {
                    "start_time": current.strftime("%I:%M %p"),
                    "end_time": slot_end.strftime("%I:%M %p"),
                    "start_time_24": current.strftime("%H:%M"),
                    "end_time_24": slot_end.strftime("%H:%M"),
                    "status": status
                }
                slots.append(slot_range)

                # Move to next slot (increment by service duration)
                current += timedelta(minutes=duration)

            return jsonify({
                "status": True,
                "aesthetician_id": aesthetician_id,
                "service_id": service_id,
                "date": date_str,
                "available_slots": slots,
                "service_duration": duration,
                "working_hours": {
                    "start_hour": shift_start_hour,
                    "start_minute": shift_start_minute,
                    "end_hour": shift_end_hour,
                    "end_minute": shift_end_minute
                }
            })

        except Exception as e:
            return jsonify({"status": False, "message": str(e)})