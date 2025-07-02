from ..controllers.base_crud_controller import BaseCRUDController
from ..models.user_model import User
from ..models.auth_model import Auth


class UserController(BaseCRUDController):
    def __ini__(self):
        super().__init__(
            model=User,
            id_field="user_id",
            updatable_fields=["first_name", "last_name", "middle_initial", "phone_number", "birthday", "image"]
        )