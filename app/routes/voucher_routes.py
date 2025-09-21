from flask import Blueprint
from app.controllers.voucher_controller import VoucherController
from ..helper.decorators import access_control
from flask_jwt_extended import jwt_required

voucher_bp = Blueprint("voucher_bp", __name__)
voucher_controller = VoucherController()


@voucher_bp.route("", methods=["POST"])
@jwt_required()
@access_control("admin", "owner")
def create_voucher():
    return voucher_controller.create()


@voucher_bp.route("", methods=["GET"])
def get_vouchers():
    return voucher_controller.get_all()


@voucher_bp.route("", methods=["PATCH"])
@jwt_required()
@access_control("admin", "owner")
def update_voucher():
    return voucher_controller.update()

@voucher_bp.route("/<string:id>", methods=["PATCH"])
@jwt_required()
@access_control("admin", "owner")
def delete_voucher(id):
    return voucher_controller.delete(id)