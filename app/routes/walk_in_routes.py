from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..controllers.walk_in_controller import (
    create_walk_in_customer,
    update_walk_in_customer,
    delete_walk_in_customer,
)
from ..helper.decorators import access_control

walk_in_routes = Blueprint("walk_in", __name__, url_prefix="/walkin")


@walk_in_routes.route("", methods=["POST"])
@jwt_required()
@access_control("admin", "owner", "customer")
def create_walk_in():
    """Create a new walk-in customer"""
    return create_walk_in_customer()


@walk_in_routes.route("", methods=["PATCH"])
@jwt_required()
@access_control("admin", "owner", "customer")
def update_walk_in():
    """Update a walk-in customer"""
    return update_walk_in_customer()


@walk_in_routes.route("", methods=["DELETE"])
@jwt_required()
@access_control("admin", "owner", "customer")
def delete_walk_in():
    """Delete a walk-in customer (soft delete)"""
    return delete_walk_in_customer()
