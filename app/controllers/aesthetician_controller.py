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
                return jsonify({"status": False, "message": "Missing body"})

            date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Fetch service duration (in minutes)
            service = Service.query.get(service_id)
            if not service:
                return jsonify({"status": False, "message": "Service not found"})

            duration = service.duration  # minutes

            # Working hours
            shift_start = datetime.combine(date, time(10, 0))
            shift_end = datetime.combine(date, time(17, 0))

            # Fetch appointments for that aesthetician (ignore the date part of start_time)
            appointments = Appointment.query.filter(
                Appointment.aesthetician_id == aesthetician_id,
                Appointment.isDeleted == False,
                Appointment.status.in_(["waiting", "on-process", "pending"])
            ).all()

            # Build available slots
            slots = []
            current = shift_start

            while current + timedelta(minutes=duration) <= shift_end:
                current_time = current.time()
                
                overlap = any(
                    (
                        # Extract time from the timestamp for comparison
                        a.start_time.time() < (current + timedelta(minutes=duration)).time()
                        and (datetime.combine(date, a.start_time.time()) + timedelta(minutes=a.duration)).time() > current_time
                    )
                    for a in appointments
                )

                if not overlap:
                    slots.append(current.strftime("%I:%M %p"))

                current += timedelta(minutes=duration)

            return jsonify({
                "status": True,
                "aesthetician_id": aesthetician_id,
                "service_id": service_id,
                "date": date_str,
                "available_slots": slots
            })

        except Exception as e:
            return jsonify({"status": False, "message": "Internal error", "error": str(e)})