from ..controllers.base_crud_controller import BaseCRUDController
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch
from ..extension import db

class AestheticianController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Aesthetician,
            id_field="aesthetician_id",
            required_fields=["first_name", "last_name", "middle_initial", "phone_number", "image", "sex", "experience"],
            updatable_fields=["first_name", "last_name", "middle_initial", "phone_number", "image", "sex", "experience", "branch_id", "availability"],
            searchable_fields=["first_name", "last_name"],
            filterable_fields={"sex": "sex", "experience": "experience", "branch": (Branch, "branch_id")},
            sortable_fields={"rate": Aesthetician.average_rate, "name":Aesthetician.first_name},
            joins=[(Branch, Branch.branch_id==Aesthetician.branch_id)]
        )
        
    def _custom_create(self, data):
        data["availability"] = "available"
        new_aesthetician = Aesthetician(**data)
        db.session.add(new_aesthetician)
        return new_aesthetician
    