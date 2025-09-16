from ..controllers.filter_analytics_controller import FilterAnalyticsController
from ..extension import db
from sqlalchemy import func, desc
from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch
from ..models.voucher_model import Voucher
from datetime import date

class AppointmentAnalyticsController:
    def __init__(self):
        pass
    
    
    def appointments_overtime(self):
        pass
    
    
    def appointments_by_service_category(self):
        query = db.session.query(Appointment.category_snapshot.label("category"), func.count(Appointment.appointment_id).label("count")).group_by(Appointment.category_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    def appointments_by_service(self):
        query = db.session.query(Appointment.category_snapshot.label("service"), func.count(Appointment.appointment_id).label("count")).group_by(Appointment.service_name_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    def appointments_by_aesthetician(self):
        query = db.session.query(Appointment.category_snapshot.label("aesthetician"), func.count(Appointment.appointment_id).label("count")).group_by(Appointment.service_name_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    
    def appointments_status(self):
        query = db.session.query(Appointment.status.label("status"), func.count(Appointment.appointment_id).label("count")).group_by(Appointment.status)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    
    def top_rated_aesthetician(self):
        query = db.session.query(func.concat(Aesthetician.first_name, " ",func.coalesce(Aesthetician.middle_initial, "")," ", Aesthetician.last_name).label("aesthetician"), Aesthetician.average_rate).order_by(desc(Aesthetician.average_rate)).limit(10)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    def top_rated_service(self):
        query = db.session.query(Service.service_name, Service.average_rate).order_by(desc(Service.average_rate)).limit(10)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]


    def top_rated_branch(self):
        query = db.session.query(Branch.branch_name, Branch.average_rate).order_by(desc(Branch.average_rate)).limit(10)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    def revenue_by_aesthetician(self):
        query = db.session.query(Appointment.aesthetician_name_snapshot.label("aesthetician"), func.sum(Appointment.to_pay).label("revenue")).group_by(Appointment.aesthetician_id, Appointment.aesthetician_name_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
        
        