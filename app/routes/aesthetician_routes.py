from flask import Blueprint
from ..controllers.aesthetician_controller import AestheticianController

aesthetician_bp = Blueprint("aesthetician", __name__)
aesthetician_controller = AestheticianController()

@aesthetician_bp.route(rule="", methods=["POST"])
def create_aesthetician():
    return aesthetician_controller.create()

@aesthetician_bp.route(rule="", methods=["GET"])
def get_aestheticians():
    return aesthetician_controller.get_all()
    
@aesthetician_bp.route(rule="", methods=["DELETE"])
def delete_aesthetician():
    return aesthetician_controller.delete()