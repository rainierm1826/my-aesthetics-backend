from ..controllers.base_crud_controller import BaseCRUDController
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch
from ..extension import db
from flask import jsonify, request

class AestheticianController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Aesthetician,
            id_field="aesthetician_id",
            required_fields=["first_name", "last_name", "middle_initial", "phone_number", "sex", "experience"],
            updatable_fields=["first_name", "last_name", "middle_initial", "phone_number", "image", "sex", "experience", "branch_id", "availability"],
            searchable_fields=["first_name", "last_name"],
            filterable_fields={"sex": "sex", "experience": "experience", "availability": "availability", "branch": (Branch, "branch_id")},
            sortable_fields={"rate": Aesthetician.average_rate, "name":Aesthetician.first_name},
            joins=[(Branch, Branch.branch_id==Aesthetician.branch_id)]
        )
    
    def get_aesthetician_name(self):
        try:
            
            branch = request.args.get("branch")
            
            query = (
                db.session.query(
                    Aesthetician.aesthetician_id,
                    Aesthetician.first_name,
                    Aesthetician.last_name,
                    Aesthetician.middle_initial,
                    Aesthetician.experience
                ).filter_by(isDeleted=False)
            )
            
            if branch:
                query = query.filter(Aesthetician.branch_id==branch, Aesthetician.availability=="available")
            
            result = query.all()

            aestheticians = [
                {
                    "aesthetician_id": a.aesthetician_id,
                    "first_name": a.first_name,
                    "last_name": a.last_name,
                    "middle_initial": a.middle_initial,
                    "experience":a.experience
                }
                for a in result
            ]

            return jsonify({"status": True, "message": "Retrieved successfully", "aesthetician": aestheticians})
        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)})

    def _custom_create(self, data):
        data["availability"] = "available"
        new_aesthetician = Aesthetician(**data)
        db.session.add(new_aesthetician)
        return new_aesthetician