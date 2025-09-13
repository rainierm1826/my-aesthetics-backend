from app import db
from ..helper.functions import generate_id
from datetime import date
from ..helper.constant import payment_method_enum, payment_status_enum, appointment_status_enum, discount_type_enum
from sqlalchemy import Float


class Appointment(db.Model):
    appointment_id = db.Column(db.String(255), primary_key=True, default=lambda:generate_id("APPOINTMENT"))
        
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
    
    # snapshots
    customer_name_snapshot = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(255))
    service_name_snapshot = db.Column(db.String(255), nullable=False)
    price_snapshot = db.Column(db.Integer, nullable=False)
    is_sale_snapshot = db.Column(db.Boolean, nullable=False, default=False)
    service_name_snapshot = db.Column(db.String(255), nullable=False)
    category_snapshot = db.Column(db.String(255), nullable=False)
    discount_type_snapshot = db.Column(discount_type_enum, nullable=True)
    discount_snapshot = db.Column(Float, nullable=True)
    discounted_price_snapshot = db.Column(Float, nullable=True)
    aesthetician_name_snapshot = db.Column(db.String(255), nullable=False)
    is_pro_snapshot = db.Column(db.Boolean, nullable=False, default=False)
    branch_name_snapshot = db.Column(db.String(255), nullable=False)
    voucher_code_snapshot = db.Column(db.String(255), nullable=True)
    voucher_discount_type_snapshot = db.Column(discount_type_enum, nullable=True, )
    voucher_discount_amount_snapshot = db.Column(db.Float, nullable=True, default=0.0)
    
    # voucher
    voucher_code = db.Column(db.String(255), db.ForeignKey("voucher.voucher_code"), nullable=True)
    
    # transaction
    down_payment_method = db.Column(payment_method_enum, nullable=True)
    down_payment = db.Column(db.Float, nullable=False, default=0.0)
    final_payment_method = db.Column(payment_method_enum, nullable=False)
    to_pay = db.Column(db.Float, nullable=False, default=0.0) # the price you're going to pay. the pro aesthetician, voucher and down payment if applicable is already deducted  
    payment_status = db.Column(payment_status_enum, nullable=False) # partial for dp and completed for complete payment


    status = db.Column(appointment_status_enum, nullable=False)
   
    isDeleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)
        
    
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
            "customer_name_snapshot": self.customer_name_snapshot,
            "aesthetician_name_snapshot": self.aesthetician_name_snapshot,
            "is_pro_snapshot": self.is_pro_snapshot,
            "phone_number": self.phone_number,
            "service_name_snapshot": self.service_name_snapshot,
            "category_snapshot": self.category_snapshot,
            "price_snapshot": self.price_snapshot,
            "is_sale_snapshot": self.is_sale_snapshot,
            "discount_type_snapshot": self.discount_type_snapshot,
            "discount_snapshot": self.discount_snapshot,
            "discounted_price_snapshot": self.discounted_price_snapshot,
            "branch_name_snapshot": self.branch_name_snapshot,
            "voucher_code_snapshot": self.voucher_code_snapshot,
            "voucher_discount_type_snapshot": self.voucher_discount_type_snapshot,
            "voucher_discount_amount_snapshot": self.voucher_discount_amount_snapshot,
            "status": self.status,
            "slot_number": self.slot_number,
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
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    

