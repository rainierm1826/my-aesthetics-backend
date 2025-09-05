from flask import Blueprint
from ..controllers.aesthetician_controller import AestheticianController
from flask_jwt_extended import jwt_required
from ..helper.decorators import access_control

aesthetician_bp = Blueprint("aesthetician", __name__)
aesthetician_controller = AestheticianController()

@aesthetician_bp.route(rule="", methods=["POST"])
# @jwt_required()
# @access_control("admin", "owner")
def create_aesthetician():
    return aesthetician_controller.create()

@aesthetician_bp.route(rule="", methods=["GET"])
def get_aestheticians():
    return aesthetician_controller.get_all()

@aesthetician_bp.route(rule="/<string:aesthetician_id>", methods=["GET"])
def get_aesthetician(aesthetician_id):
    return aesthetician_controller.get_by_id(aesthetician_id)
    
@aesthetician_bp.route(rule="", methods=["DELETE"])
# @jwt_required()
# @access_control("admin", "owner")
def delete_aesthetician():
    return aesthetician_controller.delete()

@aesthetician_bp.route(rule="", methods=["PATCH"])
# @jwt_required()
# @access_control("admin", "owner")
def update_aesthetician():
    return aesthetician_controller.update()

@aesthetician_bp.route(rule="/aesthetician-name", methods=["GET"])
def get_aesthetician_name():
    return aesthetician_controller.get_aesthetician_name()