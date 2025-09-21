from flask import Blueprint
from ..controllers.branch_controller import BranchController
from ..helper.decorators import access_control
from flask_jwt_extended import jwt_required


branch_bp = Blueprint("branch", __name__)
branch_controller = BranchController()

@branch_bp.route(rule="", methods=["GET"])
def get_branches():
    return branch_controller.get_all()

@branch_bp.route(rule="/branch-name", methods=["GET"])
def get_branch_name():
    return branch_controller.get_branch_name()

@branch_bp.route("", methods=["POST"])
@jwt_required()
@access_control("owner")
def create_branch():
    return branch_controller.create()

@branch_bp.route("/<string:id>", methods=["PATCH"])
@jwt_required()
@access_control("owner")
def delete_branch(id):
    return branch_controller.delete(id)

@branch_bp.route("", methods=["PATCH"])
@jwt_required()
@access_control("admin", "owner")
def update_branch():
    return branch_controller.update()

@branch_bp.route("<string:branch_id>", methods=["GET"])
def get_branch(branch_id):
    return branch_controller.get_by_id(branch_id)
    