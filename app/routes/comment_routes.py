from flask import Blueprint
from ..controllers.comment_controller import CommentController
from flask_jwt_extended import jwt_required

comment_bp = Blueprint("comment", __name__)

controller = CommentController()


@comment_bp.route(rule="", methods=["POST"])
@jwt_required()
def create_comment():
    return controller.create_with_auth()

@comment_bp.route(rule="", methods=["DELETE"])
@jwt_required()
def delete_comment():
    return controller.delete_with_auth() # the sign in user must be the same as the comment user

@comment_bp.route(rule="", methods=["PATCH"])
@jwt_required()
def update_comment():
    return controller.update_with_auth() # the sign in user must be the same as the comment user

@comment_bp.route(rule="", methods=["GET"])
@jwt_required()
def get_comments():
    return controller.get_by_id() # get the comments by users id

@comment_bp.route(rule="/all", methods=["GET"])
def get_all_comments():
    return controller.get_all() # get all comments. the owner can only use this
