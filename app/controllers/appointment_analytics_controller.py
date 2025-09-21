from ..controllers.filter_analytics_controller import FilterAnalyticsController
from ..extension import db
from sqlalchemy import func, desc, extract, case
from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch
from flask import request


class AppointmentAnalyticsController:
    def __init__(self):
        pass
    
    
    def appointment_overtime(self):
        group_by = request.args.get("group-by", default="year")
        if group_by == "year":
            query = db.session.query(
                extract("year", Appointment.created_at).label("year"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("year").order_by("year")


        elif group_by == "month":
            month_num = extract("month", Appointment.created_at)

            query = db.session.query(
                extract("year", Appointment.created_at).label("year"),
                case(
                    (month_num == 1, "January"),
                    (month_num == 2, "February"),
                    (month_num == 3, "March"),
                    (month_num == 4, "April"),
                    (month_num == 5, "May"),
                    (month_num == 6, "June"),
                    (month_num == 7, "July"),
                    (month_num == 8, "August"),
                    (month_num == 9, "September"),
                    (month_num == 10, "October"),
                    (month_num == 11, "November"),
                    (month_num == 12, "December"),
                ).label("month"),
                func.count(Appointment.appointment_id).label("count"),
            ).group_by("year", "month", month_num).order_by("year", month_num)

            
        elif group_by == "weekday":
            dow = extract("dow", Appointment.created_at)
            query = db.session.query(
                case(
                    (dow == 0, "Sunday"),
                    (dow == 1, "Monday"),
                    (dow == 2, "Tuesday"),
                    (dow == 3, "Wednesday"),
                    (dow == 4, "Thursday"),
                    (dow == 5, "Friday"),
                    (dow == 6, "Saturday"),
                ).label("weekday"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("weekday").order_by("weekday")

        else:
            query = db.session.query(
                Appointment.created_at.label("date"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("date").order_by("date")

        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]

    
    def appointments_by_service_category(self):
        query = db.session.query(Appointment.category_snapshot.label("category"), func.count(Appointment.appointment_id).label("count")).group_by(Appointment.category_snapshot)
        query = FilterAnalyticsController.apply_not_deleted(query, Service)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    def appointments_by_service(self):
        query = db.session.query(Appointment.service_name_snapshot.label("service"), func.count(Appointment.appointment_id).label("count")).group_by( Appointment.service_name_snapshot)
        query = FilterAnalyticsController.apply_not_deleted(query, Service)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    def appointments_by_branch(self):
        query = db.session.query(Appointment.branch_name_snapshot.label("branch"), func.count(Appointment.appointment_id).label("count")).group_by(Appointment.branch_name_snapshot)
        query = FilterAnalyticsController.apply_not_deleted(query, Branch)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    def appointments_by_aesthetician(self):
        query = db.session.query(Appointment.aesthetician_name_snapshot.label("aesthetician"), func.count(Appointment.appointment_id).label("count")).group_by(Appointment.aesthetician_name_snapshot)
        query = FilterAnalyticsController.apply_not_deleted(query, Aesthetician)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    
    def appointments_status(self):
        params = FilterAnalyticsController.get_filter_params()
        query = db.session.query(Appointment.status, func.count(Appointment.appointment_id).label("count")).group_by(Appointment.status)
        query = FilterAnalyticsController.apply_filter_branch(query, params["branch_id"])
        query = FilterAnalyticsController.apply_filter_date(query, params["year"], params["month"])
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        return [dict(row._mapping) for row in query.all()]
    
    
    def top_rated_aesthetician(self):
        query = db.session.query(func.concat(Aesthetician.first_name, " ",func.coalesce(Aesthetician.middle_initial, "")," ", Aesthetician.last_name).label("aesthetician"), Aesthetician.average_rate).group_by(Aesthetician.aesthetician_id)
        query = FilterAnalyticsController.apply_not_deleted(query, Aesthetician)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.order_by(desc(Aesthetician.average_rate)).limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    def top_rated_service(self):
        query = db.session.query(Service.service_name, Service.average_rate).group_by(Service.service_id).group_by(Service.service_id)
        query = FilterAnalyticsController.apply_not_deleted(query, Service)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.order_by(desc(Service.average_rate)).limit(10)
        return [dict(row._mapping) for row in query.all()]


    def top_rated_branch(self):
        query = db.session.query(Branch.branch_name, Branch.average_rate).group_by(Branch.branch_id).group_by(Branch.branch_id)
        query = FilterAnalyticsController.apply_not_deleted(query, Branch)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.order_by(desc(Branch.average_rate)).limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    



        
        