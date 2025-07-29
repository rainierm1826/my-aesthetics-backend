from .base_crud_controller import BaseCRUDController
from ..models.service_model import Service
from ..models.branch_model import Branch

class ServiceController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Service,
            id_field="service_id",
            required_fields=["branch_id", "service_name", "price", "category", "image"],
            searchable_fields=["service"],
            filterable_fields={"category": "category", "branch": (Branch, "branch_name")},
            updatable_fields=["service_name", "branch_id", "price", "category", "image"],
            sortable_fields={"price": Service.price, "service": Service.service_name, "rate": Service.avarage_rate},
            joins=[(Branch, Service.branch_id == Branch.branch_id)]
        )
    
