from .base_crud_controller import BaseCRUDController
from ..models.service_model import Service
from ..models.branch_model import Branch
from flask import jsonify
from ..extension import db

class ServiceController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Service,
            id_field="service_id",
            required_fields=["service_name", "price", "is_sale", "category", "image"],
            searchable_fields=["service_name"],
            filterable_fields={"category": "category", "branch": (Branch, "branch_name")},
            updatable_fields=["service_name", "branch_id", "original_price", "is_sale", "discount_percentage", "category", "image"],
            sortable_fields={"price": Service.price, "service": Service.service_name, "rate": Service.average_rate},
            joins=[(Branch, Service.branch_id == Branch.branch_id, "left")]
        )
        
    def _custom_create(self, data):
        service = Service.query.filter_by(service_name=data['service_name']).first()
        if service:
            return jsonify({"status": False, "message": "service name already exist"}), 409
        
        new_service = Service(**data)
        db.session.add(new_service)
        
        return new_service
    
        
        
    
