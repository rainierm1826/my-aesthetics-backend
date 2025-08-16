from sqlalchemy import Enum

payment_method_enum = Enum("cash", "xendit", name="payment_method_enum")
payment_status_enum = Enum("completed", "partial", "pending", name="payment_status_enum")
appointment_status_enum = Enum("cancelled", "completed", "pending", "waiting", name="appointment_status_enum")
sex_enum = Enum("male", "female", "others", name="sex_enum")
experience_enum = Enum("pro", "regular", name="experience_enum")
availability_enum = Enum("available", "working", "off-duty", "break", name="availability_enum")
role_enum = Enum("admin", "customer", "owner", name="role_enum")
day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# group_column = {
#         "year": func.extract("year", Appointment.created_at),   
#         "month": func.extract("month", Appointment.created_at), 
#         "week": func.extract("dow", Appointment.created_at),  
#         "service": Service.service_name,
#         "category": Service.category,
#         "status": Appointment.status,
#         "aesthetician": func.concat(Aesthetician.first_name, " ", Aesthetician.last_name)
#     }