from .base_crud_controller import BaseCRUDController
from ..models.branch_model import Branch
from ..models.address_model import Address
from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..extension import db
from flask import request, jsonify
from datetime import datetime, time, timedelta
from sqlalchemy import func

class BranchController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Branch,
            id_field="branch_id",
            required_fields=["branch_name", "barangay", "city", "province", "region", "lot", "slot_capacity", "opening_time", "closing_time"],
            searchable_fields=["branch_name"],
            updatable_fields=["branch_name", "barangay", "city", "province", "region", "lot", "status", "slot_capacity", "opening_time", "closing_time"],
            sortable_fields={"rate": Branch.average_rate},
            joins=[(Address, Address.address_id == Branch.address_id)]
        )
        
    def get_branch_name(self):
        try:
            result = db.session.query(Branch.branch_id, Branch.branch_name).filter_by(isDeleted=False).all()
            branches = [{"branch_id": branch.branch_id, "branch_name": branch.branch_name } for branch in result]
            response = {"status": True, "message": "Retrieved successfully", 'branch': branches}
            return jsonify(response)
        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)})
        

    def _custom_create(self, data):
        address_fields = ['region', 'province', 'city', 'barangay', 'lot']
        address_data = {}
        
        for field in address_fields:
            if field in data:
                address_data[field] = data.pop(field)
        
        if address_data:
            address = Address(**address_data)
            db.session.add(address)
            db.session.flush()  
            data['address_id'] = address.address_id
        
        branch = self.model(**data)
        db.session.add(branch)
        db.session.flush()
        return branch

    def _custom_update(self, data):
        
        instance = self.model.query.filter(getattr(self.model, self.id_field) == data[self.id_field]).first()
        # Handle nested address updates
        if "address_id" in data:
            address = Address.query.filter_by(address_id=data["address_id"]).first()  # Added .first()
            
            if address:
                address_fields = ["region", "province", "city", "barangay", "lot"]
                for field in address_fields:  # Iterate through fields, not 
                    if field in data:  
                        if hasattr(address, field):
                            setattr(address, field, data[field])
        
        # Handle direct field updates (excluding nested fields)
        for field in self.updatable_fields:
            if field in data and "." not in field:  # Skip nested fields like "address.barangay"
                setattr(instance, field, data[field])
        
        return instance

    def get_available_slots(self, branch_id):
        """
        Get available time slots for a branch based on branch slot_capacity.
        Instead of checking individual aesthetician availability, we check how many
        concurrent appointments can be scheduled at the same time based on slot_capacity.
        
        Parameters:
        - branch_id: The branch ID (from URL path)
        
        Query params:
        - service_id: The service ID (to get duration)
        - date: The date in YYYY-MM-DD format
        """
        try:
            service_id = request.args.get("service_id")
            date_str = request.args.get("date")

            if not all([branch_id, service_id, date_str]):
                return jsonify({"status": False, "message": "Missing required parameters"})

            # Fetch branch
            branch = Branch.query.get(branch_id)
            if not branch:
                return jsonify({"status": False, "message": "Branch not found"})

            slot_capacity = branch.slot_capacity
            if not slot_capacity or slot_capacity <= 0:
                return jsonify({"status": False, "message": "Invalid branch slot capacity"})

            # Parse date
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"status": False, "message": "Invalid date format. Use YYYY-MM-DD"})

            # Fetch service duration
            service = Service.query.get(service_id)
            if not service:
                return jsonify({"status": False, "message": "Service not found"})

            duration = service.duration  # minutes
            if not duration or duration <= 0:
                return jsonify({"status": False, "message": "Invalid service duration"})

            # Working hours from branch opening and closing times
            opening_time = branch.opening_time if branch.opening_time else time(10, 0)
            closing_time = branch.closing_time if branch.closing_time else time(17, 0)

            shift_start = datetime.combine(date, opening_time)
            shift_end = datetime.combine(date, closing_time)

            # Fetch all non-deleted and active appointments for that branch on the same date
            appointments = Appointment.query.filter(
                Appointment.branch_id == branch_id,
                Appointment.isDeleted == False,
                Appointment.status.in_(["waiting", "on-process", "pending"]),
                func.date(Appointment.start_time) == date
            ).all()

            # Build available slot ranges
            slots = []
            current = shift_start
            now = datetime.now()

            while current + timedelta(minutes=duration) <= shift_end:
                slot_end = current + timedelta(minutes=duration)

                # Determine slot status
                status = "available"

                # Check if slot is in the past
                if current < now:
                    status = "past-time"
                else:
                    # Count how many appointments overlap with this time slot
                    concurrent_count = 0
                    for appointment in appointments:
                        if not appointment.duration or appointment.duration <= 0:
                            continue

                        # Get appointment start time
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

                        # Calculate appointment end time
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

                # Move to next slot
                current += timedelta(minutes=duration)

            return jsonify({
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
            })

        except Exception as e:
            return jsonify({"status": False, "message": "Internal error", "error": str(e)})
    