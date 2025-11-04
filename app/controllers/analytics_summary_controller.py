from ..controllers.filter_analytics_controller import FilterAnalyticsController
from ..extension import db
from sqlalchemy import func, cast, Date
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
        query = FilterAnalyticsController.apply_is_completed(query)
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        return query.scalar() or 0
    
    def total_revenue(self):
        query = db.session.query(func.sum(Appointment.to_pay)).filter(Appointment.status=="completed")
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        return query.scalar() or 0
    
    def average_transaction_value(self):
        total_revenue = self.total_revenue()
        total_appointments = self.total_appointments()
        if total_appointments == 0:
            return 0
        return round(total_revenue / total_appointments, 2)
    
    def total_discount_given(self):
        query = db.session.query(func.sum(Appointment.discount_snapshot)).filter(
            Appointment.status=="completed",
            Appointment.discount_snapshot.isnot(None)
        )
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        result = query.scalar() or 0
        return round(result, 2)
    
    def total_voucher_usage(self):
        query = db.session.query(func.count(Appointment.appointment_id)).filter(
            Appointment.status=="completed",
            Appointment.voucher_code_snapshot.isnot(None)
        )
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        return query.scalar() or 0
    
    def avarage_service_rating(self):
        query = db.session.query(func.avg(Service.average_rate))
        query = FilterAnalyticsController.apply_not_deleted(query, Service)
        result = query.scalar()
        return round(result, 2) if result is not None else 0
    
    def avarage_branch_rating(self):
        query = db.session.query(func.avg(Branch.average_rate))
        query = FilterAnalyticsController.apply_not_deleted(query, Branch)
        result = query.scalar()
        return round(result, 2) if result is not None else 0
    
    
    def avarage_aesthetician_rating(self):
        query = db.session.query(func.avg(Aesthetician.average_rate))
        query = FilterAnalyticsController.apply_not_deleted(query, Aesthetician)
        result = query.scalar()
        return round(result, 2) if result is not None else 0
    

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
        query = FilterAnalyticsController.apply_not_deleted(query, Service)
        result = query.scalar()
        return round(result, 2) if result is not None else 0
    
    
    def total_aestheticians(self):
        params = FilterAnalyticsController.get_filter_params()
        query = db.session.query(func.count(Aesthetician.aesthetician_id))
        query = FilterAnalyticsController.apply_not_deleted(query, Aesthetician)
        query = FilterAnalyticsController.apply_filter_branch(query, params["branch_id"])
        query = FilterAnalyticsController.apply_filter_date(query, params["month"], params["year"])
        return query.scalar() or 0
    
    def total_branches(self):
        params = FilterAnalyticsController.get_filter_params()
        query = db.session.query(func.count(Branch.branch_id))
        query = FilterAnalyticsController.apply_not_deleted(query, Aesthetician)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = FilterAnalyticsController.apply_filter_branch(query, params["branch_id"])
        query = FilterAnalyticsController.apply_filter_date(query, params["month"], params["year"])
        return query.scalar() or 0
    
    
    def total_active_vouchers(self):
        query = db.session.query(func.count(Voucher.voucher_code)).filter(Voucher.valid_until > date.today())
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = FilterAnalyticsController.apply_not_deleted(query, Voucher)
        return query.scalar() or 0
    
    
    def sex_count_by_aesthetician(self):
        query = db.session.query(func.count(Aesthetician.sex).label("count"), Aesthetician.sex).group_by(Aesthetician.sex)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = FilterAnalyticsController.apply_not_deleted(query, Aesthetician)
        return [dict(row._mapping) for row in query.all()]
    
    
    def completion_rate(self):
        params = FilterAnalyticsController.get_filter_params()

        base_query = db.session.query(Appointment.appointment_id).filter(Appointment.isDeleted == False)
        
        base_query = FilterAnalyticsController.apply_filter_branch(base_query, params['branch_id'])
        base_query = FilterAnalyticsController.apply_filter_date(base_query, params['year'], params['month'])
        base_query = FilterAnalyticsController.apply_not_deleted(base_query, Appointment)

        total_appointments = base_query.count()
        
        completed_query = base_query.filter(Appointment.status == "completed")
        completed_appointments = completed_query.count()

        if total_appointments == 0:
            return 0
        
        return round((completed_appointments / total_appointments) * 100, 2)


    def cancellation_rate(self):
        params = FilterAnalyticsController.get_filter_params()

        base_query = db.session.query(Appointment.appointment_id).filter(Appointment.isDeleted == False)
        base_query = FilterAnalyticsController.apply_filter_branch(base_query, params['branch_id'])
        base_query = FilterAnalyticsController.apply_filter_date(base_query, params['year'], params['month'])
        base_query = FilterAnalyticsController.apply_not_deleted(base_query, Appointment)

        total_appointments = base_query.count()

        cancelled_query = base_query.filter(Appointment.status == "cancelled")
        cancelled_appointments = cancelled_query.count()

        if total_appointments == 0:
            return 0

        return round((cancelled_appointments / total_appointments) * 100, 2)


    def branch_completion_rate(self):
        # Total appointments per branch (excluding deleted)
        total_query = (
            db.session.query(
                Appointment.branch_id,
                func.count(Appointment.appointment_id).label("total")
            )
            .filter(Appointment.isDeleted == False)
            .group_by(Appointment.branch_id)
            .subquery()
        )

        # Completed appointments per branch (excluding deleted)
        completed_query = (
            db.session.query(
                Appointment.branch_id,
                func.count(Appointment.appointment_id).label("completed")
            )
            .filter(Appointment.status == "completed")
            .filter(Appointment.isDeleted == False)
            .group_by(Appointment.branch_id)
            .subquery()
        )

        # Join both and calculate completion rate
        result = (
            db.session.query(
                Branch.branch_name.label("branch_name"),  # live branch name
                (
                    func.coalesce(completed_query.c.completed, 0) 
                    / total_query.c.total * 100
                ).label("completion_rate")
            )
            .join(total_query, Branch.branch_id == total_query.c.branch_id)   # inner join ensures only branches with appointments appear
            .outerjoin(completed_query, completed_query.c.branch_id == total_query.c.branch_id)
            .all()
        )

        # Format result into dictionary
        return {row.branch_name: float(round(row.completion_rate, 2)) for row in result}



    def aesthetician_experience(self):
        query = (
            db.session.query(
                Aesthetician.experience,
                func.count(func.distinct(Aesthetician.aesthetician_id)).label("count")
            )
            .group_by(Aesthetician.experience)
        )
        query = FilterAnalyticsController.apply_not_deleted(query, Aesthetician)
        return [dict(row._mapping) for row in query.all()]
    
    def sale_service(self):
        params = FilterAnalyticsController.get_filter_params()
        query = db.session.query(func.count(Service.service_id).label("count"))
        query = query.filter(Service.is_sale==True, Service.isDeleted==False)
        query = FilterAnalyticsController.apply_not_deleted(query, Service)
        query = FilterAnalyticsController.apply_filter_branch(query, params["branch_id"])
        query = FilterAnalyticsController.apply_filter_date(query, params["month"], params["year"])
        result = query.scalar()
        return round(result, 2) if result is not None else 0
    
    def service_per_category(self):
        params = FilterAnalyticsController.get_filter_params()
        query = db.session.query(Service.category, func.count(Service.service_id).label("count")).group_by(Service.category)
        query = FilterAnalyticsController.apply_not_deleted(query, Service)
        query = FilterAnalyticsController.apply_filter_branch(query, params["branch_id"])
        return [dict(row._mapping) for row in query.all()]
    
    

    def appointments_per_branch(self):
        daily_counts = (
            db.session.query(
                Appointment.branch_name_snapshot.label("branch"),
                cast(Appointment.created_at, Date).label("day"),
                func.count(Appointment.appointment_id).label("daily_count")
            )
            .filter(Appointment.isDeleted.is_(False), Appointment.status=="completed")
            .group_by(Appointment.branch_id, Appointment.branch_name_snapshot, cast(Appointment.created_at, Date))
            .subquery()
        )

        query = (
            db.session.query(
                daily_counts.c.branch,
                func.round(func.avg(daily_counts.c.daily_count)).label("daily_average")
            )
            .group_by(daily_counts.c.branch)
        )

        return [dict(row._mapping) for row in query.all()]