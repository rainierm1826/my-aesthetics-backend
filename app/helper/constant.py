from sqlalchemy import Enum


# enums
payment_method_enum = Enum("cash", "e-wallet", "bank-transfer", "credit-card", "debit-card", name="payment_method_enum")
payment_status_enum = Enum("completed", "partial", "pending", name="payment_status_enum")
branch_status_enum = Enum("active", "closed", name="branch_status_enum")
appointment_status_enum = Enum("cancelled", "completed", "on-process", "waiting", name="appointment_status_enum")
sex_enum = Enum("male", "female", "others", name="sex_enum")
experience_enum = Enum("pro", "regular", name="experience_enum")
availability_enum = Enum("available", "working", "off-duty", "break", name="availability_enum")
role_enum = Enum("admin", "customer", "owner", name="role_enum")
discount_type_enum = Enum("percentage", "fixed", name="discount_type_enum")

# dates
day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']