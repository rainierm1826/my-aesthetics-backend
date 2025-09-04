from .base_crud_controller import BaseCRUDController
from ..models.service_model import Service
from ..models.branch_model import Branch
from flask import jsonify, request
from ..extension import db
from sqlalchemy import or_

class ServiceController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Service,
            id_field="service_id",
            required_fields=["service_name", "price", "is_sale", "category", "image"],
            searchable_fields=["service_name"],
            filterable_fields={"category": "category", "branch": (Branch, "branch_id")},
            updatable_fields=["service_name", "branch_id", "original_price", "is_sale", "discount_percentage", "category", "image"],
            sortable_fields={"price": Service.price, "service": Service.service_name, "rate": Service.average_rate},
            joins=[(Branch, Service.branch_id == Branch.branch_id, "left")]
        )
    
    def get_service_name(self):
        try:
            branch = request.args.get("branch")
            
            query = (
                db.session.query(
                    Service.service_id,
                    Service.service_name
                )
            )
            if branch and branch.lower() != "all":
                query = query.filter(
                    or_(Service.branch_id == branch, Service.branch_id == None)
                )
            
            result = query.all()

            services = [
                {
                    "service_id": a.service_id,
                    "service_name":a.service_name
                }
                for a in result
            ]

            return jsonify({"status": True, "message": "Retrieved successfully", "service": services})
        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)})
    
    def _apply_filters(self, query):
        # Category filter works normally
        category = request.args.get("category")
        if category:
            query = query.filter(Service.category == category)

        # Branch filter: include services for that branch OR global (NULL)
        branch = request.args.get("branch")
        if branch and branch.lower() != "all":
            query = query.filter(
                or_(Service.branch_id == branch, Service.branch_id == None)
            )

        return query

    
    def _custom_create(self, data):
        service = Service.query.filter_by(service_name=data['service_name']).first()
        if service:
            return jsonify({"status": False, "message": "service name already exist"}), 409
        
        new_service = Service(**data)
        db.session.add(new_service)
        
        return new_service
    
        
        
    
