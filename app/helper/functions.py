from flask import jsonify
from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..models.branch_model import Branch
from ..extension import db
from sqlalchemy.sql import func


def does_exist(model, column_name, value, label):
    field = getattr(model, column_name)
    exist = model.query.filter(field==value).first()
    if exist:
        return jsonify({"status":False, "message":f"{label} already exist"}), 409
    
    return None

def update_average_rating(model, model_id, rating_field, foreign_key_field):
    avg_rating = db.session.query(func.avg(getattr(Appointment, rating_field))).filter(
        getattr(Appointment, foreign_key_field) == model_id,
        getattr(Appointment, rating_field) != None
    ).scalar()

    instance = db.session.get(model, model_id)
    if instance:
        instance.avarage_rate = round(avg_rating or 0.0, 2)
        db.session.commit()

def filter_sales(group_by, year=None, month=None):
    
    # Dictionary to determine how to group the data: by year, month, or day of week
    group_column = {
        "year": func.extract("year", Appointment.created_at),   # Groups by year (e.g., 2024)
        "month": func.extract("month", Appointment.created_at), # Groups by month (1–12)
        "week": func.extract("dow", Appointment.created_at),    # Groups by day of week (0=Sunday, 6=Saturday)
    }[group_by]  # Selects the grouping based on the query parameter

    
    # Query that calculates total sales based on the chosen group
    sales = db.session.query(
        group_column.label(group_by),            # Labels the group (year/month/week)
        func.sum(Service.price).label("total")   # Sums all service prices under that group
    ).join(Service).filter(Appointment.status == "completed") # Join Appointment to Service to access the price

    # Optional filters based on year and/or month
    if year:
        sales = sales.filter(func.extract("year", Appointment.created_at) == year)

    if month:
        sales = sales.filter(func.extract("month", Appointment.created_at) == month)

    # Group the results and sort them in order
    return sales.group_by(group_column).order_by(group_column).all()


