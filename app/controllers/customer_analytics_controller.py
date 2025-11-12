from ..extension import db
from sqlalchemy import func, desc, case, and_
from ..models.user_model import User
from ..models.walk_in_model import WalkIn
from ..models.appointment_model import Appointment
from flask import request, jsonify
from datetime import datetime, timedelta

class CustomerAnalyticsController:
    def __init__(self):
        pass

    def total_customers(self):
        """Get total count of all customers (online + walk-in)"""
        online_customers = db.session.query(func.count(User.user_id)).filter(
            User.isDeleted == False
        ).scalar() or 0
        
        walkin_customers = db.session.query(func.count(WalkIn.walk_in_id)).filter(
            WalkIn.isDeleted == False
        ).scalar() or 0
        
        return online_customers + walkin_customers

    def active_customers(self, days=30):
        """Get count of customers with appointments in last X days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get unique online customers with recent appointments
        online_active = db.session.query(func.count(func.distinct(Appointment.user_id))).filter(
            Appointment.user_id.isnot(None),
            Appointment.isDeleted == False,
            Appointment.created_at >= cutoff_date
        ).scalar() or 0
        
        # Get unique walk-in customers with recent appointments
        walkin_active = db.session.query(func.count(func.distinct(Appointment.walk_in_id))).filter(
            Appointment.walk_in_id.isnot(None),
            Appointment.isDeleted == False,
            Appointment.created_at >= cutoff_date
        ).scalar() or 0
        
        return online_active + walkin_active

    def customer_retention_rate(self):
        """Calculate percentage of customers with 2+ completed appointments"""
        # Online customers with 2+ completed appointments
        online_repeat = db.session.query(
            Appointment.user_id
        ).filter(
            Appointment.user_id.isnot(None),
            Appointment.isDeleted == False,
            Appointment.status == "completed"
        ).group_by(Appointment.user_id).having(
            func.count(Appointment.appointment_id) >= 2
        ).count()
        
        # Walk-in customers with 2+ completed appointments
        walkin_repeat = db.session.query(
            Appointment.walk_in_id
        ).filter(
            Appointment.walk_in_id.isnot(None),
            Appointment.isDeleted == False,
            Appointment.status == "completed"
        ).group_by(Appointment.walk_in_id).having(
            func.count(Appointment.appointment_id) >= 2
        ).count()
        
        total_repeat = online_repeat + walkin_repeat
        total_customers = self.total_customers()
        
        if total_customers == 0:
            return 0
        
        return round((total_repeat / total_customers) * 100, 2)

    def average_customer_lifetime_value(self):
        """Calculate average total spending per customer"""
        # Total revenue from online customers
        online_revenue = db.session.query(
            func.sum(Appointment.to_pay)
        ).filter(
            Appointment.user_id.isnot(None),
            Appointment.isDeleted == False,
            Appointment.status == "completed"
        ).scalar() or 0
        
        # Total revenue from walk-in customers
        walkin_revenue = db.session.query(
            func.sum(Appointment.to_pay)
        ).filter(
            Appointment.walk_in_id.isnot(None),
            Appointment.isDeleted == False,
            Appointment.status == "completed"
        ).scalar() or 0
        
        total_revenue = online_revenue + walkin_revenue
        total_customers = self.total_customers()
        
        if total_customers == 0:
            return 0
        
        return round(total_revenue / total_customers, 2)

    def customer_detail(self):
        """Get detailed analytics for a specific customer"""
        customer_id = request.args.get("customer_id")
        customer_type = request.args.get("type", default="online")  # online or walkin
        
        # Normalize customer_type (convert "walk-in" to "walkin")
        if customer_type == "walk-in":
            customer_type = "walkin"
        
        if not customer_id:
            return jsonify({"status": False, "message": "customer_id required"}), 400
        
        if customer_type == "online":
            customer = User.query.filter_by(user_id=customer_id, isDeleted=False).first()
            if not customer:
                return jsonify({"status": False, "message": "Customer not found"}), 404
            
            customer_name = f"{customer.first_name} {customer.middle_initial or ''} {customer.last_name}".strip()
            customer_phone = customer.phone_number
            joined_date = customer.created_at
            
        else:  # walkin
            customer = WalkIn.query.filter_by(walk_in_id=customer_id, isDeleted=False).first()
            if not customer:
                return jsonify({"status": False, "message": "Walk-in customer not found"}), 404
            
            customer_name = f"{customer.first_name} {customer.middle_initial or ''} {customer.last_name}".strip()
            customer_phone = customer.phone_number
            joined_date = customer.created_at
        
        # Get all appointments for this customer
        if customer_type == "online":
            appointments = Appointment.query.filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False
            ).all()
        else:
            appointments = Appointment.query.filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False
            ).all()
        
        # Basic stats
        total_appointments = len(appointments)
        completed_appointments = len([a for a in appointments if a.status == "completed"])
        cancelled_appointments = len([a for a in appointments if a.status == "cancelled"])
        
        # Revenue stats
        if customer_type == "online":
            total_spent_query = db.session.query(func.sum(Appointment.to_pay)).filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            )
        else:
            total_spent_query = db.session.query(func.sum(Appointment.to_pay)).filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            )
        
        total_spent = total_spent_query.scalar() or 0
        average_transaction = total_spent / completed_appointments if completed_appointments > 0 else 0
        
        # Service preferences
        if customer_type == "online":
            favorite_services = db.session.query(
                Appointment.service_name_snapshot.label("service"),
                func.count(Appointment.appointment_id).label("count")
            ).filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            ).group_by("service").order_by(desc("count")).limit(5)
        else:
            favorite_services = db.session.query(
                Appointment.service_name_snapshot.label("service"),
                func.count(Appointment.appointment_id).label("count")
            ).filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            ).group_by("service").order_by(desc("count")).limit(5)
        
        # Aesthetician preferences
        if customer_type == "online":
            favorite_aestheticians = db.session.query(
                Appointment.aesthetician_name_snapshot.label("aesthetician"),
                func.count(Appointment.appointment_id).label("count")
            ).filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            ).group_by("aesthetician").order_by(desc("count")).limit(5)
        else:
            favorite_aestheticians = db.session.query(
                Appointment.aesthetician_name_snapshot.label("aesthetician"),
                func.count(Appointment.appointment_id).label("count")
            ).filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            ).group_by("aesthetician").order_by(desc("count")).limit(5)
        
        # Branch preferences
        if customer_type == "online":
            favorite_branches = db.session.query(
                Appointment.branch_name_snapshot.label("branch"),
                func.count(Appointment.appointment_id).label("count")
            ).filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            ).group_by("branch").order_by(desc("count")).limit(5)
        else:
            favorite_branches = db.session.query(
                Appointment.branch_name_snapshot.label("branch"),
                func.count(Appointment.appointment_id).label("count")
            ).filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            ).group_by("branch").order_by(desc("count")).limit(5)
        
        # Last appointment (exclude ones with invalid 1900-01-01 dates)
        if customer_type == "online":
            last_appointment = Appointment.query.filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False
            ).order_by(desc(Appointment.start_time)).first()
        else:
            last_appointment = Appointment.query.filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False
            ).order_by(desc(Appointment.start_time)).first()
        
        # Days since last appointment
        days_since_last = None
        if last_appointment:
            try:
                # Check if start_time is valid (not 1900-01-01)
                if last_appointment.start_time and last_appointment.start_time > datetime(1950, 1, 1):
                    appointment_date = last_appointment.start_time.date()
                elif last_appointment.created_at:
                    # Fall back to created_at if start_time is invalid
                    appointment_date = last_appointment.created_at
                else:
                    appointment_date = None
                
                if appointment_date:
                    today = datetime.now().date()
                    days_diff = (today - appointment_date).days
                    days_since_last = abs(days_diff) if days_diff >= 0 else None
            except Exception as e:
                # If there's any error in calculation, set to None
                days_since_last = None
        
        # Appointment timeline (last 10 appointments)
        if customer_type == "online":
            appointment_history = db.session.query(
                Appointment.appointment_id,
                Appointment.start_time,
                Appointment.status,
                Appointment.service_name_snapshot,
                Appointment.aesthetician_name_snapshot,
                Appointment.to_pay
            ).filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False
            ).order_by(desc(Appointment.start_time)).limit(10)
        else:
            appointment_history = db.session.query(
                Appointment.appointment_id,
                Appointment.start_time,
                Appointment.status,
                Appointment.service_name_snapshot,
                Appointment.aesthetician_name_snapshot,
                Appointment.to_pay
            ).filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False
            ).order_by(desc(Appointment.start_time)).limit(10)
        
        return jsonify({
            "status": True,
            "customer": {
                "id": customer_id,
                "name": customer_name,
                "type": customer_type,
                "phone": customer_phone,
                "joined_date": joined_date.isoformat() if joined_date else None
            },
            "stats": {
                "total_appointments": total_appointments,
                "completed_appointments": completed_appointments,
                "cancelled_appointments": cancelled_appointments,
                "total_spent": float(total_spent),
                "average_transaction": float(average_transaction),
                "days_since_last_appointment": days_since_last
            },
            "preferences": {
                "favorite_services": [dict(row._mapping) for row in favorite_services.all()],
                "favorite_aestheticians": [dict(row._mapping) for row in favorite_aestheticians.all()],
                "favorite_branches": [dict(row._mapping) for row in favorite_branches.all()]
            },
            "appointment_history": [
                {
                    **dict(row._mapping),
                    "start_time": row.start_time.isoformat() if isinstance(row.start_time, datetime) else row.start_time
                }
                for row in appointment_history.all()
            ]
        })

    def customer_appointments_timeline(self):
        """Get appointment timeline for a customer"""
        customer_id = request.args.get("customer_id")
        customer_type = request.args.get("type", default="online")
        
        # Normalize customer_type (convert "walk-in" to "walkin")
        if customer_type == "walk-in":
            customer_type = "walkin"
        
        if not customer_id:
            return jsonify({"status": False, "message": "customer_id required"}), 400
        
        if customer_type == "online":
            query = db.session.query(
                Appointment.appointment_id,
                Appointment.start_time,
                Appointment.status,
                Appointment.service_name_snapshot,
                Appointment.aesthetician_name_snapshot,
                Appointment.branch_name_snapshot,
                Appointment.to_pay,
                Appointment.payment_status
            ).filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False
            ).order_by(desc(Appointment.start_time))
        else:
            query = db.session.query(
                Appointment.appointment_id,
                Appointment.start_time,
                Appointment.status,
                Appointment.service_name_snapshot,
                Appointment.aesthetician_name_snapshot,
                Appointment.branch_name_snapshot,
                Appointment.to_pay,
                Appointment.payment_status
            ).filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False
            ).order_by(desc(Appointment.start_time))
        
        return jsonify({
            "status": True,
            "appointments": [
                {
                    **dict(row._mapping),
                    "start_time": row.start_time.isoformat() if isinstance(row.start_time, datetime) else row.start_time
                }
                for row in query.all()
            ]
        })

    def customer_spending_by_service(self):
        """Customer spending breakdown by service"""
        customer_id = request.args.get("customer_id")
        customer_type = request.args.get("type", default="online")
        
        # Normalize customer_type (convert "walk-in" to "walkin")
        if customer_type == "walk-in":
            customer_type = "walkin"
        
        if not customer_id:
            return jsonify({"status": False, "message": "customer_id required"}), 400
        
        if customer_type == "online":
            query = db.session.query(
                Appointment.service_name_snapshot.label("service"),
                func.count(Appointment.appointment_id).label("appointment_count"),
                func.sum(Appointment.to_pay).label("total_spent"),
                func.avg(Appointment.to_pay).label("average_spent")
            ).filter(
                Appointment.user_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            ).group_by("service").order_by(desc("total_spent"))
        else:
            query = db.session.query(
                Appointment.service_name_snapshot.label("service"),
                func.count(Appointment.appointment_id).label("appointment_count"),
                func.sum(Appointment.to_pay).label("total_spent"),
                func.avg(Appointment.to_pay).label("average_spent")
            ).filter(
                Appointment.walk_in_id == customer_id,
                Appointment.isDeleted == False,
                Appointment.status == "completed"
            ).group_by("service").order_by(desc("total_spent"))
        
        return jsonify({
            "status": True,
            "spending": [dict(row._mapping) for row in query.all()]
        })
