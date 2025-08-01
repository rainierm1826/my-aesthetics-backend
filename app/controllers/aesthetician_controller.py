from ..controllers.base_crud_controller import BaseCRUDController
from ..models.aesthetician_model import Aesthetician
from ..models.branch_model import Branch

class AestheticianController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Aesthetician,
            id_field="aesthetician_id",
            required_fields=["first_name", "last_name", "middle_initial", "phone_number", "image", "sex", "experience"],
            updatable_fields=["first_name", "last_name", "middle_initial", "phone_number", "image", "sex", "experience", "branch_id"],
            searchable_fields=["first_name", "last_name"],
            filterable_fields={"sex": "sex", "experience": "experience", "branch": (Branch, "branch_name")},
            sortable_fields={"rate": Aesthetician.avarage_rate, "name":Aesthetician.first_name},
            joins=[(Branch, Branch.branch_id==Aesthetician.branch_id)]
        )
    