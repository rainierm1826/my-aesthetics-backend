from app import db
from ..helper.functions import generate_id
from datetime import datetime, timezone
from ..helper.constant import payment_method_enum, payment_status_enum, appointment_status_enum

class Appointment(db.Model):
    appointment_id = db.Column(db.String(255), primary_key=True, default=generate_id("APPOINTMENT"))
        
    # foreign keys
    user_id = db.Column(db.String(255), db.ForeignKey("user.user_id"), nullable=True)
    walk_in_id = db.Column(db.String(255), db.ForeignKey("walk_in.walk_in_id"), nullable=True)
    branch_id = db.Column(db.String(255), db.ForeignKey("branch.branch_id"), nullable=False)
    aesthetician_id = db.Column(db.String(255), db.ForeignKey("aesthetician.aesthetician_id"), nullable=False)
    service_id = db.Column(db.String(255), db.ForeignKey("service.service_id"), nullable=False)
    
    slot_number = db.Column(db.Integer, nullable=False)
    
    # ratings
    service_rating = db.Column(db.Float, nullable=True)
    branch_rating = db.Column(db.Float, nullable=True)
    aesthetician_rating = db.Column(db.Float, nullable=True)
    
    # comments
    service_comment = db.Column(db.Text, nullable=True)
    branch_comment = db.Column(db.Text, nullable=True)
    aesthetician_comment = db.Column(db.Text, nullable=True)
    
    # voucher
    voucher_code = db.Column(db.String(255), db.ForeignKey("voucher.voucher_code"), nullable=True)
    
    # payment
    down_payment_method = db.Column(payment_method_enum, nullable=True)
    down_payment = db.Column(db.Float, nullable=False, default=0.0)
    final_payment_method = db.Column(payment_method_enum, nullable=False)
    original_amount = db.Column(db.Float, nullable=False, default=0.0) # the original price. pro aesthetician and voucher not included
    to_pay = db.Column(db.Float, nullable=False, default=0.0) # the price you're going to pay. the pro aesthetician, voucher and down payment if applicable is already deducted  
    payment_status = db.Column(payment_status_enum, nullable=False) # partial for dp and completed for complete payment


    status = db.Column(appointment_status_enum, nullable=False)
   
   
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
        
    
    # relationships
    user = db.relationship("User", backref="appointments")
    walk_in = db.relationship("WalkIn", backref="appointments")
    branch = db.relationship("Branch", backref="appointments")
    aesthetician = db.relationship("Aesthetician", backref="appointments")
    service = db.relationship("Service", backref="appointments")
    voucher = db.relationship("Voucher", backref="appointments")
    
    
    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "user": {
                "user_id": self.user.user_id,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "middle_initial": self.user.middle_initial,
            } if self.user else None,
            "walk_in": {
                "walk_in_id": self.walk_in.walk_in_id,
                "first_name": self.walk_in.first_name,
                "last_name": self.walk_in.last_name,
                "middle_initial": self.walk_in.middle_initial,
            } if self.walk_in else None,
            "branch": {
                "branch_id": self.branch_id,
                "branch_name": self.branch.branch_name if self.branch.branch_id else None
            },
            "aesthetician": {
                "aesthetician_id": self.aesthetician.aesthetician_id,
                "first_name": self.aesthetician.first_name,
                "last_name": self.aesthetician.last_name,
                "middle_initial": self.aesthetician.middle_initial,
                "experience": self.aesthetician.experience,
            },
            "service": {
                "service_id": self.service.service_id,
                "service_name": self.service.service_name,
                "final_price": self.service.final_price,
                "category": self.service.category,
            },
            "status": self.status,
            "branch_rating": self.branch_rating,
            "service_rating": self.service_rating,
            "aesthetician_rating": self.aesthetician_rating,
            "service_comment": self.service_comment,
            "branch_comment": self.branch_comment,
            "aesthetician_comment": self.aesthetician_comment,
            "down_payment_method": self.down_payment_method,
            "down_payment": self.down_payment,
            "final_payment_method": self.final_payment_method,
            "to_pay": self.to_pay,
            "payment_status": self.payment_status,
            "voucher_code": self.voucher_code,
            "discount_amount": self.voucher.discount_amount if self.voucher else 0.0,
            "original_amount": self.original_amount,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    

