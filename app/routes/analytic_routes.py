from flask import Blueprint
from flask_jwt_extended import jwt_required
from ..helper.decorators import access_control
from ..controllers.analytics_controller import AnalyticsController
from ..models.appointment_model import Appointment
from flask import request

analytics_bp = Blueprint('analytics_bp', __name__)
analytics_controller = AnalyticsController()

@analytics_bp.route("/sales/group-sales", methods=["GET"])
def get_group_sales():
    group_by = request.args.get("group-by", "branch")
    branch = request.args.get("branch")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    filter = [Appointment.status == "completed"]
    return analytics_controller.get_total_sales(group_by=group_by, filter=filter, aggregate_field=Appointment.to_pay,branch=branch, year=year, month=month)


@analytics_bp.route("/sales/total-sales", methods=["GET"])
def get_total_sales():
    branch = request.args.get("branch")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    return analytics_controller.get_total_sales(branch=branch, year=year, month=month, aggregate_field=Appointment.to_pay)


@analytics_bp.route("/appointment/total-appointment-status", methods=["GET"])
def get_total_appointment():
    filter = [Appointment.status == "completed"]
    branch = request.args.get("branch")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    return analytics_controller.count_field(branch=branch, year=year, month=month, aggregate_field=Appointment.status, filter=filter)


@analytics_bp.route("/appointment/group-appointment-status", methods=["GET"])
def get_group_appointment():
    group_by = request.args.get("group-by", "branch")
    branch = request.args.get("branch")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    return analytics_controller.count_field(group_by=group_by, branch=branch, year=year, month=month, aggregate_field=Appointment.status)