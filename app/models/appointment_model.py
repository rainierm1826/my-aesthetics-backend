from app import db
from ..helper.functions import generate_id
from datetime import date
from ..helper.constant import payment_method_enum, payment_status_enum, appointment_status_enum, discount_type_enum
from .base_mixin import SoftDeleteMixin

class Appointment(db.Model, SoftDeleteMixin):
    __tablename__ = "appointment"

    appointment_id = db.Column(
        db.String(255), primary_key=True, default=lambda: generate_id("APPOINTMENT")
    )
    
    # foreign keys
    user_id = db.Column(db.String(255), db.ForeignKey("user.user_id"), nullable=True)
    walk_in_id = db.Column(db.String(255), db.ForeignKey("walk_in.walk_in_id"), nullable=True)
    branch_id = db.Column(db.String(255), db.ForeignKey("branch.branch_id"), nullable=False)
    
    # customer info
    customer_name_snapshot = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(255))
    branch_name_snapshot = db.Column(db.String(255), nullable=False)
    
    # voucher info
    voucher_code = db.Column(db.String(255), db.ForeignKey("voucher.voucher_code"), nullable=True)
    voucher_code_snapshot = db.Column(db.String(255), nullable=True)
    voucher_discount_type_snapshot = db.Column(discount_type_enum, nullable=True)
    voucher_discount_amount_snapshot = db.Column(db.Float, nullable=True, default=0.0)
    
    # transaction
    final_payment_method = db.Column(payment_method_enum, nullable=False)
    to_pay = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(payment_status_enum, nullable=False)
    
    # overall ratings/comments (optional summary)
    branch_rating = db.Column(db.Float, nullable=True)
    branch_comment = db.Column(db.Text, nullable=True)
    
    # appointment time & status
    status = db.Column(appointment_status_enum, nullable=False)
    isDeleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Date, default=date.today())
    updated_at = db.Column(db.Date, default=date.today(), onupdate=date.today())
    
    # relationships
    user = db.relationship("User", backref="appointments")
    walk_in = db.relationship("WalkIn", backref="appointments")
    branch = db.relationship("Branch", backref="appointments")
    voucher = db.relationship("Voucher", backref="appointments")
    
    # relationship to services (one-to-many)
    services = db.relationship(
        "AppointmentService",
        back_populates="appointment",
        cascade="all, delete-orphan"
    )
    
    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "customer_name_snapshot": self.customer_name_snapshot,
            "phone_number": self.phone_number,
            "branch_name_snapshot": self.branch_name_snapshot,
            "status": self.status,
            "branch_rating": self.branch_rating,
            "branch_comment": self.branch_comment,
            "final_payment_method": self.final_payment_method,
            "to_pay": self.to_pay,
            "payment_status": self.payment_status,
            "voucher_code": self.voucher_code,
            "voucher_code_snapshot": self.voucher_code_snapshot,
            "voucher_discount_type_snapshot": self.voucher_discount_type_snapshot,
            "voucher_discount_amount_snapshot": self.voucher_discount_amount_snapshot,
            "user_id": self.user_id,
            "walk_in_id": self.walk_in_id,
            "branch_id": self.branch_id,
            "services": [s.to_dict() for s in self.services]  # include all linked services
        }

# Fix for SQLAlchemy relationship import order
from .appointment_services_model import AppointmentService
