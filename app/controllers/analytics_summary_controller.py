from ..controllers.filter_analytics_controller import FilterAnalyticsController
from ..extension import db
from sqlalchemy import func
from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch
from ..models.voucher_model import Voucher
from datetime import date
import statistics

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
    
    import statistics

    def avarage_overall_rating(self):
        branch = self.avarage_branch_rating()
        service = self.avarage_service_rating()
        aesthetician = self.avarage_aesthetician_rating()

        values = [branch, service, aesthetician]
        valid_values = [v for v in values if v is not None]

        if not valid_values:
            return 0

        return round(statistics.mean(valid_values), 2)

    
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
    
    
    def completion_rate(self):
        params = FilterAnalyticsController.get_filter_params()

        base_query = db.session.query(Appointment.appointment_id)
        base_query = FilterAnalyticsController.apply_filter_branch(base_query, params['branch_id'])
        base_query = FilterAnalyticsController.apply_filter_date(base_query, params['year'], params['month'])

        total_appointments = base_query.count()

        completed_query = base_query.filter(Appointment.status == "completed")
        completed_appointments = completed_query.count()

        if total_appointments == 0:
            return 0

        return round((completed_appointments / total_appointments)*100, 2)

    
    def cancellation_rate(self):
        params = FilterAnalyticsController.get_filter_params()

        base_query = db.session.query(Appointment.appointment_id)
        base_query = FilterAnalyticsController.apply_filter_branch(base_query, params['branch_id'])
        base_query = FilterAnalyticsController.apply_filter_date(base_query, params['year'], params['month'])

        total_appointments = base_query.count()

        completed_query = base_query.filter(Appointment.status == "cancelled")
        completed_appointments = completed_query.count()

        if total_appointments == 0:
            return 0

        return round((completed_appointments / total_appointments)*100, 2)