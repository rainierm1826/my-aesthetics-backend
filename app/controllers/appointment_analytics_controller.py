from ..controllers.filter_analytics_controller import FilterAnalyticsController
from ..controllers.base_filter_controller import BasicFilterAnalyticsController
from ..extension import db
from sqlalchemy import func, desc, extract, case
from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch
from flask import request
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from ..helper.linear_regression_model import linear_regression_model


class AppointmentAnalyticsController:
    def __init__(self):
        pass
    

    def appointment_overtime(self):
        group_by = request.args.get("group-by", default="year")
        predict = request.args.get("predict", default="true").lower()=="true"
        
        
        if group_by == "year":
            query = db.session.query(
                extract("year", Appointment.created_at).label("year"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("year").order_by("year")

        elif group_by == "month":
            month_num = extract("month", Appointment.created_at)
            query = db.session.query(
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
                month_num.label("month_num")
            ).group_by("month", "month_num").order_by("month_num")

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
                func.count(Appointment.appointment_id).label("count"),
                dow.label("dow_num")
            ).group_by("weekday", "dow_num").order_by("dow_num")

        else:
            query = db.session.query(
                Appointment.created_at.label("date"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("date").order_by("date")

        query = FilterAnalyticsController.apply_is_completed(query)
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        data = [dict(row._mapping) for row in query.all()]

        if predict:
            return linear_regression_model(data, group_by=group_by, y_values="count")
        else:
            return data
    
    
    def appointment_accuracy_check(self):
        group_by = request.args.get("group-by", default="year")

        if group_by == "year":
            query = db.session.query(
                extract("year", Appointment.created_at).label("year"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("year").order_by("year")

        elif group_by == "month":
            query = db.session.query(
                extract("month", Appointment.created_at).label("month_num"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("month_num").order_by("month_num")

        elif group_by == "weekday":
            query = db.session.query(
                extract("dow", Appointment.created_at).label("dow_num"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("dow_num").order_by("dow_num")

        else:
            query = db.session.query(
                Appointment.created_at.label("date"),
                func.count(Appointment.appointment_id).label("count")
            ).group_by("date").order_by("date")

        query = FilterAnalyticsController.apply_filters_from_request(query)
        data = [dict(row._mapping) for row in query.all()]
        if not data:
            return {"metrics": {}}

        df = pd.DataFrame(data)

        # X and y
        if group_by == "year":
            X = np.arange(len(df)).reshape(-1, 1)
        elif group_by == "month":
            X = df["month_num"].values.reshape(-1, 1)
        elif group_by == "weekday":
            X = df["dow_num"].values.reshape(-1, 1)
        else:
            X = np.arange(len(df)).reshape(-1, 1)
        y = df["count"].values

        if len(df) > 3:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

            model = LinearRegression().fit(X_train, y_train)
            y_pred = model.predict(X_test)

            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            return {"metrics": {"MAE": mae, "MSE": mse, "R2": r2}}
        else:
            return {"metrics": {"MAE": None, "MSE": None, "R2": None}}
    
    def appointments_by_service_category(self):
        query = db.session.query(Appointment.category_snapshot.label("category"), func.count(Appointment.appointment_id).label("count")).group_by(Appointment.category_snapshot)
        query = FilterAnalyticsController.apply_is_completed(query)
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        return [dict(row._mapping) for row in query.all()]
    
    def appointments_by_service(self):
        query = (
            db.session.query(
                Service.service_name.label("service"),  # live service name
                func.count(Appointment.appointment_id).label("count")
            )
            .join(Service, Appointment.service_id == Service.service_id)
            .group_by(Service.service_name)
        )

        query = FilterAnalyticsController.apply_is_completed(query)
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)

        return [dict(row._mapping) for row in query.all()]

    
    def appointments_by_branch(self):
        query = (
            db.session.query(
                Branch.branch_name.label("branch"),  # live branch name
                func.count(Appointment.appointment_id).label("count")
            )
            .join(Branch, Appointment.branch_id == Branch.branch_id)
            .group_by(Branch.branch_name)
        )

        query = FilterAnalyticsController.apply_is_completed(query)
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)

        return [dict(row._mapping) for row in query.all()]

    
    def appointments_by_aesthetician(self):
        query = (
        db.session.query(
            func.concat(Aesthetician.first_name, " ", Aesthetician.middle_initial, " ", Aesthetician.last_name).label("aesthetician"),
            func.count(Appointment.appointment_id).label("count")
        )
        .join(Aesthetician, Appointment.aesthetician_id == Aesthetician.aesthetician_id)
        .group_by(Aesthetician.first_name, Aesthetician.last_name, Aesthetician.middle_initial)
        )

        query = FilterAnalyticsController.apply_is_completed(query)
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)

        return [dict(row._mapping) for row in query.all()]

    
    
    def appointments_status(self):
        params = FilterAnalyticsController.get_filter_params()
        query = db.session.query(Appointment.status, func.count(Appointment.appointment_id).label("count")).group_by(Appointment.status)
        query = FilterAnalyticsController.apply_filter_branch(query, params["branch_id"])
        query = FilterAnalyticsController.apply_filter_date(query, params["month"], params["year"])
        query = FilterAnalyticsController.apply_not_deleted(query, Appointment)
        return [dict(row._mapping) for row in query.all()]
    
    
    def top_rated_aesthetician(self):
        query = db.session.query(
            func.concat(Aesthetician.first_name, " ", func.coalesce(Aesthetician.middle_initial, ""), " ", Aesthetician.last_name).label("aesthetician"), 
            Aesthetician.average_rate
        ).filter(Aesthetician.average_rate.isnot(None)).group_by(Aesthetician.aesthetician_id)
        query = FilterAnalyticsController.apply_not_deleted(query, Aesthetician)
        query = BasicFilterAnalyticsController.apply_filters_from_request(query, Aesthetician)
        query = query.order_by(desc(Aesthetician.average_rate)).limit(10)
        return [dict(row._mapping) for row in query.all()]

    def top_rated_service(self):
        query = db.session.query(Service.service_name, Service.average_rate).filter(Service.average_rate.isnot(None)).group_by(Service.service_id)
        query = FilterAnalyticsController.apply_not_deleted(query, Service)        
        query = BasicFilterAnalyticsController.apply_filters_from_request(query, Service)
        query = query.order_by(desc(Service.average_rate)).limit(10)
        return [dict(row._mapping) for row in query.all()]

    def top_rated_branch(self):
        query = db.session.query(Branch.branch_name, Branch.average_rate).group_by(Branch.branch_id)
        query = FilterAnalyticsController.apply_not_deleted(query, Branch)
        query = BasicFilterAnalyticsController.apply_filters_from_request(query, Branch)
        query = query.order_by(desc(Branch.average_rate)).limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    



        
        