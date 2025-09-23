from ..controllers.filter_analytics_controller import FilterAnalyticsController
from ..extension import db
from sqlalchemy import func, extract, case
from ..models.appointment_model import Appointment
from flask import request
from ..helper.linear_regression_model import linear_regression_model
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


class SalesAnalyticsController:
    def __init__(self):
        pass
    
    def revenue_overtime(self):
        group_by = request.args.get("group-by", default="year")
        predict = request.args.get("predict", default="true").lower()=="true"

        if group_by == "year":
            query = db.session.query(
                extract("year", Appointment.created_at).label("year"),
                func.sum(Appointment.to_pay).label("revenue")
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
                func.sum(Appointment.to_pay).label("revenue"),
                month_num.label("month_num")
            ).group_by("month", month_num).order_by(month_num)


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
                dow.label("dow_num"),
                func.sum(Appointment.to_pay).label("revenue")
            ).group_by("weekday", "dow_num").order_by("dow_num")

        else: 
            query = db.session.query(
                Appointment.created_at.label("date"),
                func.sum(Appointment.to_pay).label("revenue")
            ).group_by("date").order_by("date")

        query = FilterAnalyticsController.apply_filters_from_request(query)
        data = [dict(row._mapping) for row in query.all()]
        
        if predict:
            return linear_regression_model(data, group_by=group_by, y_values="revenue")
        return data
    
    def sales_accuracy_check(self):
        group_by = request.args.get("group-by", default="year")

        if group_by == "year":
            query = db.session.query(
                extract("year", Appointment.created_at).label("year"),
                func.sum(Appointment.to_pay).label("revenue")
            ).group_by("year").order_by("year")

        elif group_by == "month":
            query = db.session.query(
                extract("month", Appointment.created_at).label("month_num"),
                func.sum(Appointment.to_pay).label("revenue")
            ).group_by("month_num").order_by("month_num")

        elif group_by == "weekday":
            query = db.session.query(
                extract("dow", Appointment.created_at).label("dow_num"),
                func.sum(Appointment.to_pay).label("revenue")
            ).group_by("dow_num").order_by("dow_num")

        else:
            query = db.session.query(
                Appointment.created_at.label("date"),
                func.sum(Appointment.to_pay).label("revenue")
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

        y = df["revenue"].values  # fix

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
    
    def revenue_by_branch(self):
        query = db.session.query(Appointment.branch_name_snapshot.label("branch"), func.sum(Appointment.to_pay).label("revenue")).group_by(Appointment.branch_id, Appointment.branch_name_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    def revenue_by_category(self):
        query = db.session.query(Appointment.category_snapshot, func.sum(Appointment.to_pay).label("revenue")).group_by(Appointment.category_snapshot)
        query = FilterAnalyticsController.apply_filters_from_request(query)
        query = query.limit(10)
        return [dict(row._mapping) for row in query.all()]
    
    
    