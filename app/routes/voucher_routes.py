from flask import Blueprint
from app.controllers.voucher_controller import VoucherController

voucher_bp = Blueprint("voucher_bp", __name__)
voucher_controller = VoucherController()


@voucher_bp.route("", methods=["POST"])
def create_voucher():
    return voucher_controller.create()


@voucher_bp.route("", methods=["GET"])
def get_vouchers():
    return voucher_controller.get_all()


@voucher_bp.route("", methods=["PATCH"])
def update_voucher():
    return voucher_controller.update()

@voucher_bp.route("", methods=["DELETE"])
def delete_voucher():
    return voucher_controller.delete()