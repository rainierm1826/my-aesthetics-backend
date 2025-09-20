from ..controllers.analytics_summary_controller import AnalyticsSummaryController
from ..controllers.appointment_analytics_controller import AppointmentAnalyticsController
from ..controllers.sales_analytics_controller import SalesAnalyticsController
from flask import Blueprint, jsonify

analytics_bp = Blueprint("analytics", __name__)
summary_controller = AnalyticsSummaryController()
appointment_analytics_controller = AppointmentAnalyticsController()
sales_analytics_controller = SalesAnalyticsController()


# summary
@analytics_bp.route(rule="/appointment/summary", methods=["GET"])
def get_appointment_summary():
    return jsonify({
        "total_appointments": summary_controller.total_appointments(),
        "avarage_overall_rating": summary_controller.avarage_overall_rating(),
        "completion_rate":summary_controller.completion_rate(),
        "cancellation_rate":summary_controller.cancellation_rate()
    })
    
# "average_service_rating": summary_controller.avarage_service_rating(),
# "average_aesthetician_rating": summary_controller.avarage_aesthetician_rating(),
# "total_service": summary_controller.total_services(),
# "total_branches": summary_controller.total_branches(),
# "total_aestheticians": summary_controller.total_aestheticians(),
# "total_active_vouchers": summary_controller.total_active_vouchers(),
# "sex-count-by-aesthetician": summary_controller.sex_count_by_aesthetician(),


@analytics_bp.route(rule="/sales/summary", methods=["GET"])
def get_sales_summary():
    return jsonify({
        "total_revenue": summary_controller.total_revenue(),
    })




# appointments
@analytics_bp.route(rule="/appointments", methods=["GET"])
def get_appointment_analytics():
    return jsonify({
        "appointments_overtime": appointment_analytics_controller.appointment_overtime(),
        "appointments_by_service_category": appointment_analytics_controller.appointments_by_service_category(),
        "appointments_by_service": appointment_analytics_controller.appointments_by_service(),
        "appointments_by_branch": appointment_analytics_controller.appointments_by_branch(),
        "appointments_by_aesthetician": appointment_analytics_controller.appointments_by_aesthetician(),
        "appointments_status": appointment_analytics_controller.appointments_status(),
        "top_rated_aesthetician": appointment_analytics_controller.top_rated_aesthetician(),
        "top_rated_service": appointment_analytics_controller.top_rated_service(),
        "top_rated_branch": appointment_analytics_controller.top_rated_branch()
    })


# sales
@analytics_bp.route(rule="/sales", methods=["GET"])
def get_revenue_summary():
    return jsonify({
        "revenue_overtime": sales_analytics_controller.revenue_overtime(),
        "revenue_by_aesthetician": sales_analytics_controller.revenue_by_aesthetician(),
        "revenue_by_service": sales_analytics_controller.revenue_by_service(),
        "revenue_by_category": sales_analytics_controller.revenue_by_category(),
        "payment_popularity": sales_analytics_controller.payment_popularity(),
        "revenue_by_branch": sales_analytics_controller.revenue_by_branch()
    })
    
@analytics_bp.route(rule="/branch", methods=["GET"])
def get_branch_analytics():
    return jsonify({
        "branch_completion_rate": summary_controller.branch_completion_rate(),
        "average_branch_rating": summary_controller.avarage_branch_rating(),
    })



@analytics_bp.route(rule="/aesthetician", methods=["GET"])
def get_aesthetician_analytics():
    return jsonify({
        "aesthetician_experience": summary_controller.aesthetician_experience(),
        "average_aesthetician_rating": summary_controller.avarage_aesthetician_rating(),
        "total_aestheticians": summary_controller.total_aestheticians(),
    })
    

@analytics_bp.route(rule="/service", methods=["GET"])
def get_service_analytics():
    return jsonify({
        "average_aesthetician_rating":summary_controller.avarage_service_rating(),
        "service_per_category": summary_controller.service_per_category(),
        "sale_service": summary_controller.sale_service(),
        "total_aestheticians": summary_controller.total_services(),
    })

