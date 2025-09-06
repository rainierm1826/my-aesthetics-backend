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
            required_fields=["branch_name", "image", "address"],
            searchable_fields=["branch_name"],
            updatable_fields=["branch_name", "image", "address.barangay", "address.city", "address.province", "address.region", "address.lot"],
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
        
    def create(self):
        try:
            data = request.form.to_dict()
            branch = Branch.query.filter_by(branch_name=data["branch_name"]).first()
            if branch:
                return jsonify({"status": False, "message": "branch name already exist"}), 409
            return super().create()
            
        except Exception as e:
            print(str(e))
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500

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
        print(data)  
        return branch

    def _custom_update(self, data):
        instance = self.model.query.filter(getattr(self.model, self.id_field) == data[self.id_field]).first()
        
        if "address" in data and instance.address:
            address_data = data["address"]
            for field, value in address_data.items():
                if hasattr(instance.address, field):
                    setattr(instance.address, field, value)
        
        for field in self.updatable_fields:
            if field in data and "." not in field:  
                setattr(instance, field, data[field])
        
        return instance