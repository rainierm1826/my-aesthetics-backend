import smtplib, ssl, string, random, os
from datetime import datetime, timezone
from email.mime.text import MIMEText
from flask import render_template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def convert_formdata_types(form_data):
    converted_data = {}
    
    for key, value in form_data.items():
        if value is None or not isinstance(value, str):
            converted_data[key] = value
            continue
            
        value = value.strip()
        
        if value.lower() in ('true', 'false'):
            converted_data[key] = value.lower() == 'true'
        
        elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            converted_data[key] = int(value)
        
        elif is_float(value):
            converted_data[key] = float(value)        
        else:
            converted_data[key] = value
    
    return converted_data


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def generate_voucher_code():
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"AESTHETICS-{random_chars}"

def generate_id(prefix):
    year = datetime.now(timezone.utc).strftime("%y")  
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{year}-{random_chars}"

def generate_otp():
    return ''.join(random.choices("0123456789", k=6))


def send_email_otp(to_email, otp, expiry=10):
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return {"status": False, "message": "Email credentials not configured"}

    # Render the template (just like for Flask pages)
    html_content = render_template("otp_email.html", otp=otp, expiry=expiry)
    text_content = f"Your OTP code is: {otp}\nThis code will expire in {expiry} minutes."

    # Build the email
    message = MIMEMultipart("alternative")
    message["From"] = f"MY Aesthetics Brow Studio"
    message["To"] = to_email
    message["Subject"] = "🔑 Account Verification Code"
    message.attach(MIMEText(text_content, "plain"))
    message.attach(MIMEText(html_content, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)

        return {"status": True, "message": f"OTP email sent to {to_email}"}
    except Exception as e:
        return {"status": False, "message": str(e)}

            
    

def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return False
    return True

    



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
    
    # if aggregate == "sum":
    #     agg_func = func.sum(Service.price)
    # if aggregate == "count":
    #     agg_func = func.count(Service.) 
    
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