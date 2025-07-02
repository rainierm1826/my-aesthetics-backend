from flask import Blueprint, request, jsonify
from app.models.service_model import Service
from app.models.branch_model import Branch
from app import db
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from ..controllers.service_controller import ServiceController


service_bp = Blueprint("service", __name__)
service_controller = ServiceController()

@service_bp.route(rule="", methods=["POST"])
def create_service():
    return service_controller.create()

@service_bp.route(rule="", methods=["GET"])
def get_services():
    return service_controller.get_all()

@service_bp.route(rule="", methods=["DELETE"])
def delete_service():
    return service_controller.delete()
