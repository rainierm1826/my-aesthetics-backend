from flask import Blueprint
from ..controllers.branch_controller import BranchController
from ..helper.decorators import access_control
from flask_jwt_extended import jwt_required


branch_bp = Blueprint("branch", __name__)
branch_controller = BranchController()

@branch_bp.route(rule="", methods=["GET"])
@jwt_required()
@access_control("admin", "owner")
def get_branches():
    return branch_controller.get_all()

@branch_bp.route("/", methods=["POST"])
def create_branch():
    return branch_controller.create()

@branch_bp.route("/", methods=["DELETE"])
def delete_branch():
    return branch_controller.delete()

@branch_bp.route("/", methods=["PATCH"])
def update_branch():
    return branch_controller.update()