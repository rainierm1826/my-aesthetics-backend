from flask import jsonify
import random
import string


def generate_voucher_code():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"aesthetics-{random_chars}"



#     instance = db.session.get(model, model_id)
#     if instance:
#         instance.avarage_rate = round(avg_rating or 0.0, 2)
#         db.session.commit()

# def total_sales_overtime(group_by, branch=None, year=None, month=None):
#     group_field = group_column[group_by]
    
#     sales = db.session.query(
#         group_field.label(group_by),
#         func.sum(Service.price).label("total")
#     ) \
#     .select_from(Appointment) \
#     .join(Service, Appointment.service_id == Service.service_id) \
#     .join(Branch, Appointment.branch_id == Branch.branch_id) \
#     .filter(Appointment.status == "completed") \
#     .group_by(group_field)
    
#     if year:
#         sales = sales.filter(func.extract("year", Appointment.created_at) == year)

#     if month:
#         sales = sales.filter(func.extract("month", Appointment.created_at) == month)
    
#     if branch:
#         sales = sales.filter(Branch.branch_name.ilike(f"%{branch}%"))

#     return sales.group_by(group_field).order_by(group_field).all()

# def count_appointment_overtime(group_by, branch=None, year=None, month=None):
#     group_field = group_column[group_by]
    
#     appointment_count = db.session.query(
#         group_field.label(group_by),
#         func.count(Appointment.appointment_id).label("count")
#     ) \
#     .select_from(Appointment) \
#     .join(Service, Appointment.service_id == Service.service_id) \
#     .join(Branch, Appointment.branch_id == Branch.branch_id) \
#     .filter(Appointment.status == "completed") \
#     .group_by(group_field)
    
#     if year:
#         appointment_count = appointment_count.filter(func.extract("year", Appointment.created_at) == year)

#     if month:
#         appointment_count = appointment_count.filter(func.extract("month", Appointment.created_at) == month)
    
#     if branch:
#         appointment_count = appointment_count.filter(Branch.branch_name.ilike(f"%{branch}%"))

#     return appointment_count.group_by(group_field).order_by(group_field).all()

# def count_status_overtime(group_by, branch=None, year=None, month=None):
#     group_field = group_column[group_by]
    
#     appointment_count = db.session.query(
#         group_field.label(group_by),
#         func.count(Appointment.status).label("status_count")
#     ) \
#     .select_from(Appointment) \
#     .join(Branch, Appointment.branch_id == Branch.branch_id) \
#     .group_by(group_field)
    
#     if year:
#         appointment_count = appointment_count.filter(func.extract("year", Appointment.created_at) == year)

#     if month:
#         appointment_count = appointment_count.filter(func.extract("month", Appointment.created_at) == month)
    
#     if branch:
#         appointment_count = appointment_count.filter(Branch.branch_name.ilike(f"%{branch}%"))

#     return appointment_count.group_by(group_field).order_by(group_field).all()

# def service_popularity(branch=None, year=None, month=None):
#     group_field = Service.service_name

#     appointment_count = db.session.query(
#         group_field.label("service"),
#         func.count(Appointment.appointment_id).label("popularity_count")
#     ) \
#     .select_from(Appointment) \
#     .join(Service, Appointment.service_id == Service.service_id) \
#     .join(Branch, Appointment.branch_id == Branch.branch_id) \
#     .filter(Appointment.status == "completed") \
#     .group_by(group_field)
    
#     if year:
#         appointment_count = appointment_count.filter(func.extract("year", Appointment.created_at) == year)

#     if month:
#         appointment_count = appointment_count.filter(func.extract("month", Appointment.created_at) == month)
    
#     if branch:
#         appointment_count = appointment_count.filter(Branch.branch_name.ilike(f"%{branch}%"))

#     return appointment_count.group_by(group_field).order_by(group_field).all()

# def total_sales_service(group_by, branch=None, year=None, month=None):
    
#     group_field = group_column[group_by]

#     sales = db.session.query(
#         group_field.label(group_by),
#         func.sum(Service.price).label("total")
#     ) \
#     .select_from(Appointment) \
#     .join(Service, Appointment.service_id == Service.service_id) \
#     .join(Branch, Appointment.branch_id == Branch.branch_id) \
#     .filter(Appointment.status == "completed") \
#     .group_by(group_field)

#     if year:
#         sales = sales.filter(func.extract("year", Appointment.created_at) == year)

#     if month:
#         sales = sales.filter(func.extract("month", Appointment.created_at) == month)
    
#     if branch:
#         sales = sales.filter(Branch.branch_name.ilike(f"%{branch}%"))

#     return sales.group_by(group_field).order_by(group_field).all()

# def total_sales_aesthetician(group_by, aggregate, branch=None, year=None, month=None, limit=None):
#     group_field = group_column[group_by]
    
#     # if aggregate == "sum":
#     #     agg_func = func.sum(Service.price)
#     # if aggregate == "count":
#     #     agg_func = func.count(Service.) 
    
#     sales = db.session.query(
#         group_field.label(group_by),
#         func.sum(Service.price).label("total")
#     ) \
#     .select_from(Appointment) \
#     .join(Service, Appointment.service_id == Service.service_id) \
#     .join(Branch, Appointment.branch_id == Branch.branch_id) \
#     .join(Aesthetician, Appointment.aesthetician_id == Aesthetician.aesthetician_id) \
#     .filter(Appointment.status == "completed") \
#     .group_by(group_field)
    
#     if year:
#         sales = sales.filter(func.extract("year", Appointment.created_at) == year)

#     if month:
#         sales = sales.filter(func.extract("month", Appointment.created_at) == month)
    
#     if branch:
#         sales = sales.filter(Branch.branch_name.ilike(f"%{branch}%"))

#     return sales.group_by(group_field).order_by(group_field).limit(limit).all()