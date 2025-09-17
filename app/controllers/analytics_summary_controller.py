from ..controllers.filter_analytics_controller import FilterAnalyticsController
from ..extension import db
from sqlalchemy import func
from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch
from ..models.voucher_model import Voucher
from datetime import date

class AnalyticsSummaryController:
    def __init__(self):
        pass
        
    def total_appointments(self):
        query = db.session.query(func.count(Appointment.appointment_id)).filter(Appointment.status=="completed")
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    def total_revenue(self):
        query = db.session.query(func.sum(Appointment.to_pay)).filter(Appointment.status=="completed")
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    def avarage_service_rating(self):
        query = db.session.query(func.avg(Service.average_rate))
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    def avarage_branch_rating(self):
        query = db.session.query(func.avg(Branch.average_rate))
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    
    def avarage_aesthetician_rating(self):
        query = db.session.query(func.avg(Aesthetician.average_rate))
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    def total_services(self):
        query = db.session.query(func.count(Service.service_id))
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    
    def total_aestheticians(self):
        query = db.session.query(func.count(Aesthetician.aesthetician_id))
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    def total_branches(self):
        query = db.session.query(func.count(Branch.branch_id))
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    
    def total_active_vouchers(self):
        query = db.session.query(func.count(Voucher.voucher_code)).filter(Voucher.valid_until > date.today())
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return query.scalar() or 0
    
    
    def sex_count_by_aesthetician(self):
        query = db.session.query(func.count(Aesthetician.sex).label("count"), Aesthetician.sex).group_by(Aesthetician.sex)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    
    
    