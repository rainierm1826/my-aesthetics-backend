from .base_crud_controller import BaseCRUDController
from ..models.branch_model import Branch
from ..models.address_model import Address
from ..extension import db
from flask import request, jsonify
import cloudinary.uploader

class BranchController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Branch,
            id_field="branch_id",
            required_fields=["branch_name", "barangay", "city", "province", "region", "lot"],
            searchable_fields=["branch_name"],
            updatable_fields=["branch_name", "barangay", "city", "province", "region", "lot", "status"],
            sortable_fields={"rate": Branch.average_rate},
            joins=[(Address, Address.address_id == Branch.address_id)]
        )
        
    def get_branch_name(self):
        try:
            result = db.session.query(Branch.branch_id, Branch.branch_name).filter_by(isDeleted=False).all()
            branches = [{"branch_id": branch.branch_id, "branch_name": branch.branch_name } for branch in result]
            response = {"status": True, "message": "Retrieved successfully", 'branch': branches}
            return jsonify(response)
        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)})
        

    def _custom_create(self, data):
        address_fields = ['region', 'province', 'city', 'barangay', 'lot']
        address_data = {}
        
        for field in address_fields:
            if field in data:
                address_data[field] = data.pop(field)
        
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
        
        instance = self.model.query.filter(getattr(self.model, self.id_field) == data[self.id_field]).first()
        # Handle nested address updates
        if "address_id" in data:
            address = Address.query.filter_by(address_id=data["address_id"]).first()  # Added .first()
            
            if address:
                address_fields = ["region", "province", "city", "barangay", "lot"]
                for field in address_fields:  # Iterate through fields, not 
                    if field in data:  
                        if hasattr(address, field):
                            setattr(address, field, data[field])
        
        # Handle direct field updates (excluding nested fields)
        for field in self.updatable_fields:
            if field in data and "." not in field:  # Skip nested fields like "address.barangay"
                setattr(instance, field, data[field])
        
        return instance
        

    