from .base_crud_controller import BaseCRUDController
from ..models.branch_model import Branch
from ..models.address_model import Address
from ..extension import db
from flask import request, jsonify

class BranchController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Branch,
            id_field="branch_id",
            required_fields=["branch_name", "image", "address"],
            searchable_fields=["branch_name"],
            updatable_fields=["branch_name", "image", "address.barangay", "address.city", "address.province", "address.region", "address.lot"],
            sortable_fields={"rate": Branch.average_rate},
            joins=[(Address, Address.address_id == Branch.address_id)]
        )
    
    def create(self):
        data = request.json
        branch = Branch.query.filter_by(branch_name=data["branch_name"]).first()
        if branch:
            return jsonify({"status": False, "message": "branch name already exist"}), 409
        return super().create()

    def _custom_create(self, data):
        address_data = data.pop("address", None)
        if address_data:
            address = Address(**address_data)
            db.session.add(address)
            db.session.flush()  
            data['address_id'] = address.address_id
        branch = self.model(**data)
        db.session.add(branch)
        db.session.flush()  
        return branch

    def _custom_update(self, data):
        # Get the instance from the base controller
        instance = self.model.query.filter(getattr(self.model, self.id_field) == data[self.id_field]).first()
        
        # Handle nested address updates
        if "address" in data and instance.address:
            address_data = data["address"]
            for field, value in address_data.items():
                if hasattr(instance.address, field):
                    setattr(instance.address, field, value)
        
        # Handle direct field updates (excluding nested fields)
        for field in self.updatable_fields:
            if field in data and "." not in field:  # Skip nested fields like "address.barangay"
                setattr(instance, field, data[field])
        
        return instance