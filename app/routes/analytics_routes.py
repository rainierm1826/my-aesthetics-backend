from ..controllers.analytics_summary_controller import AnalyticsSummaryController
from flask import Blueprint, jsonify

analytics_bp = Blueprint("analytics", __name__)
summary_controller = AnalyticsSummaryController()

@analytics_bp.route(rule="/total-appointment", methods=["GET"])
def get_total_appointments():
    return jsonify({"total_appointments": summary_controller.total_appointments()})


@analytics_bp.route(rule="/total-revenue", methods=["GET"])
def get_total_revenue():
    return jsonify({"total_revenue": summary_controller.total_revenue()})

@analytics_bp.route(rule="/avarage-service-rating", methods=["GET"])
def get_avarage_service_rating():
    return jsonify({"avarage-service-rating": summary_controller.avarage_service_rating()})

@analytics_bp.route(rule="/avarage-aesthetician-rating", methods=["GET"])
def get_avarage_aesthetician_rating():
    return jsonify({"avarage-aesthetician-rating": summary_controller.avarage_aesthetician_rating()})

@analytics_bp.route(rule="/avarage-branch-rating", methods=["GET"])
def get_avarage_branch_rating():
    return jsonify({"avarage-branch-rating": summary_controller.avarage_branch_rating()})