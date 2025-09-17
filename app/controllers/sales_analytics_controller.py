from ..controllers.filter_analytics_controller import FilterAnalyticsController
from ..extension import db
from sqlalchemy import func, extract, case
from ..models.appointment_model import Appointment
from flask import request


class SalesAnalyticsController:
    def __init__(self):
        pass
    
    def revenue_overtime(self):
        group_by = request.args.get("group-by", default="year")
        if group_by == "year":
            query = db.session.query(
                extract("year", Appointment.created_at).label("year"),
                func.sum(Appointment.to_pay).label("revenue")
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
                func.sum(Appointment.to_pay).label("count"),
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
                func.sum(Appointment.to_pay).label("revenue")
            ).group_by("weekday").order_by("weekday")

        else: 
            query = db.session.query(
                Appointment.created_at.label("date"),
                func.sum(Appointment.to_pay).label("revenue")
            ).group_by("date").order_by("date")

        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]

    def payment_popularity(self):
        query = db.session.query(Appointment.final_payment_method, func.count(Appointment.appointment_id).label("count")).group_by(Appointment.final_payment_method)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]

    
    def revenue_by_aesthetician(self):
        query = db.session.query(Appointment.aesthetician_name_snapshot.label("aesthetician"), func.sum(Appointment.to_pay).label("revenue")).group_by(Appointment.aesthetician_id, Appointment.aesthetician_name_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    def revenue_by_service(self):
        query = db.session.query(Appointment.service_name_snapshot.label("service"), func.sum(Appointment.to_pay).label("revenue")).group_by(Appointment.service_id, Appointment.service_name_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    def revenue_by_category(self):
        query = db.session.query(Appointment.category_snapshot, func.sum(Appointment.to_pay).label("revenue")).group_by(Appointment.category_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    
    