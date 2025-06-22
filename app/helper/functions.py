from flask import jsonify
from ..models.appointment_model import Appointment
from ..models.aesthetician_model import Aesthetician
from ..extension import db
from sqlalchemy.sql import func


def does_exist(model, column_name, value, label):
    field = getattr(model, column_name)
    exist = model.query.filter(field==value).first()
    if exist:
        return jsonify({"status":False, "message":f"{label} already exist"}), 409
    
    return None


def update_aesthetician_average_rating(aesthetician_id):
    avg_rating = db.session.query(func.avg(Appointment.rating)).filter(
        Appointment.aesthetician_id == aesthetician_id,
        Appointment.rating != None
    ).scalar()

    aesthetician = Aesthetician.query.get(aesthetician_id)

    if aesthetician:
        aesthetician.avarage_rate = round(avg_rating or 0.0, 2)  # ✅ correct field name
        db.session.commit()

    