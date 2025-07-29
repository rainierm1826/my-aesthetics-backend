from ..controllers.base_crud_controller import BaseCRUDController
from ..models.comment_model import Comment
from ..models.user_model import User

class CommentController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Comment,
            id_field="comment_id",
            required_fields=["comment"],
            updatable_fields=["comment"],
            joins=[(User, User.user_id==Comment.user_id)]
        )
        
    
    