from ..controllers.analytics_summary_controller import AnalyticsSummaryController
from ..controllers.appointment_analytics_controller import AppointmentAnalyticsController
from ..controllers.sales_analytics_controller import SalesAnalyticsController
from flask import Blueprint, jsonify

analytics_bp = Blueprint("analytics", __name__)
summary_controller = AnalyticsSummaryController()
appointment_analytics_controller = AppointmentAnalyticsController()
sales_analytics_controller = SalesAnalyticsController()

# summary
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



# appointments
@analytics_bp.route(rule="/appointments-overtime", methods=["GET"])
def get_appointments_overtime():
    return jsonify(appointment_analytics_controller.appointment_overtime())

@analytics_bp.route(rule="/appointments-by-service-category", methods=["GET"])
def get_appointments_by_service_category():
    return jsonify(appointment_analytics_controller.appointments_by_service_category())

@analytics_bp.route(rule="/appointments-by-service", methods=["GET"])
def get_appointments_by_service():
    return jsonify(appointment_analytics_controller.appointments_by_service())

@analytics_bp.route(rule="/appointments-by-aesthetician", methods=["GET"])
def get_appointments_by_aesthetician():
    return jsonify(appointment_analytics_controller.appointments_by_aesthetician())

@analytics_bp.route(rule="/appointments-status", methods=["GET"])
def get_appointments_status():
    return jsonify(appointment_analytics_controller.appointments_status())


@analytics_bp.route(rule="/top-rated-aesthetician", methods=["GET"])
def get_top_rated_aesthetician():
    return jsonify(appointment_analytics_controller.top_rated_aesthetician())


@analytics_bp.route(rule="/top-rated-service", methods=["GET"])
def get_top_rated_service():
    return jsonify(appointment_analytics_controller.top_rated_service())


@analytics_bp.route(rule="/top-rated-branch", methods=["GET"])
def get_top_rated_branch():
    return jsonify(appointment_analytics_controller.top_rated_branch())



# sales
@analytics_bp.route(rule="/revenue-overtime", methods=["GET"])
def get_revenue_overtime():
    return jsonify(sales_analytics_controller.revenue_overtime())


@analytics_bp.route(rule="/revenue-by-aesthetician", methods=["GET"])
def get_revenue_by_aesthetician():
    return jsonify(sales_analytics_controller.revenue_by_aesthetician())


@analytics_bp.route(rule="/revenue-by-service", methods=["GET"])
def get_revenue_by_service():
    return jsonify(sales_analytics_controller.revenue_by_service())


@analytics_bp.route(rule="/revenue-by-category", methods=["GET"])
def get_revenue_by_category():
    return jsonify(sales_analytics_controller.revenue_by_category())

@analytics_bp.route(rule="/get-payment-popularity", methods=["GET"])
def get_payment_popularity():
    return jsonify(sales_analytics_controller.payment_popularity())