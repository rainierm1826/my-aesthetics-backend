from app import db
from ..helper.constant import discount_type_enum
from sqlalchemy import Float
from uuid import uuid4


class AppointmentService(db.Model):
    __tablename__ = "appointment_service"

    id = db.Column(
        db.String(255),
        primary_key=True,
        default=lambda:str(uuid4())
    )
    
    appointment_id = db.Column(
        db.String(255),
        db.ForeignKey("appointment.appointment_id"),
        nullable=False
    )

    service_id = db.Column(
        db.String(255),
        db.ForeignKey("service.service_id"),
        nullable=False
    )

    aesthetician_id = db.Column(
        db.String(255),
        db.ForeignKey("aesthetician.aesthetician_id"),
        nullable=True
    )

    # Snapshots for each service
    service_name_snapshot = db.Column(db.String(255), nullable=False)
    price_snapshot = db.Column(db.Integer, nullable=False)
    is_sale_snapshot = db.Column(db.Boolean, nullable=False, default=False)
    category_snapshot = db.Column(db.String(255), nullable=False)
    discount_type_snapshot = db.Column(discount_type_enum, nullable=True)
    discount_snapshot = db.Column(Float, nullable=True)
    discounted_price_snapshot = db.Column(Float, nullable=True)
    aesthetician_name_snapshot = db.Column(db.String(255), nullable=True)
    is_pro_snapshot = db.Column(db.Boolean, nullable=False, default=False)
    duration_snapshot = db.Column(db.Integer, nullable=True)

    # NEW: individual scheduling per service
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(50), nullable=False, default="pending")

    # ratings and comments per service
    service_rating = db.Column(db.Float, nullable=True)
    service_comment = db.Column(db.Text, nullable=True)
    aesthetician_rating = db.Column(db.Float, nullable=True)
    aesthetician_comment = db.Column(db.Text, nullable=True)
    branch_rating = db.Column(db.Float, nullable=True)
    branch_comment = db.Column(db.Text, nullable=True)

    # relationships
    appointment = db.relationship("Appointment", back_populates="services")

    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "service_id": self.service_id,
            "aesthetician_id": self.aesthetician_id,
            "service_name_snapshot": self.service_name_snapshot,
            "price_snapshot": self.price_snapshot,
            "is_sale_snapshot": self.is_sale_snapshot,
            "category_snapshot": self.category_snapshot,
            "discount_type_snapshot": self.discount_type_snapshot,
            "discount_snapshot": self.discount_snapshot,
            "discounted_price_snapshot": self.discounted_price_snapshot,
            "aesthetician_name_snapshot": self.aesthetician_name_snapshot,
            "is_pro_snapshot": self.is_pro_snapshot,
            "duration_snapshot": self.duration_snapshot,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.service_status,  # Map service_status to status for frontend
            "service_status": self.service_status,
            "service_rating": self.service_rating,
            "service_comment": self.service_comment,
            "aesthetician_rating": self.aesthetician_rating,
            "aesthetician_comment": self.aesthetician_comment,
            "branch_rating": self.branch_rating,
            "branch_comment": self.branch_comment,
        }
