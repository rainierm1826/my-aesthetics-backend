from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..models.aesthetician_model import Aesthetician
from sqlalchemy.sql import func


group_column = {
        "year": func.extract("year", Appointment.created_at),   
        "month": func.extract("month", Appointment.created_at), 
        "week": func.extract("dow", Appointment.created_at),  
        "service": Service.service_name,
        "category": Service.category,
        "status": Appointment.status,
        "aesthetician": func.concat(Aesthetician.first_name, " ", Aesthetician.last_name)
    }