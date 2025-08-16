from flask import Blueprint
from ..controllers.branch_controller import BranchController
from ..helper.decorators import access_control
from flask_jwt_extended import jwt_required


branch_bp = Blueprint("branch", __name__)
branch_controller = BranchController()

@branch_bp.route(rule="", methods=["GET"])
def get_branches():
    return branch_controller.get_all()

@branch_bp.route("/", methods=["POST"])
# @jwt_required()
# @access_control("owner")
def create_branch():
    return branch_controller.create()

@branch_bp.route("/", methods=["DELETE"])
# @jwt_required()
# @access_control("owner")
def delete_branch():
    return branch_controller.delete()

@branch_bp.route("/", methods=["PATCH"])
# @jwt_required()
# @access_control("owner")
def update_branch():
    return branch_controller.update()