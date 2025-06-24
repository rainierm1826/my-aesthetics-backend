from flask import jsonify
from ..models.appointment_model import Appointment
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
