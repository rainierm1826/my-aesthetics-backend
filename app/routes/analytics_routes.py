from ..controllers.analytics_summary_controller import AnalyticsSummaryController
from ..controllers.appointment_analytics_controller import AppointmentAnalyticsController
from ..controllers.sales_analytics_controller import SalesAnalyticsController
from flask import Blueprint, jsonify

analytics_bp = Blueprint("analytics", __name__)
summary_controller = AnalyticsSummaryController()
appointment_analytics_controller = AppointmentAnalyticsController()
sales_analytics_controller = SalesAnalyticsController()

# summary
@analytics_bp.route(rule="/summary", methods=["GET"])
def get_summary():
    return jsonify({
        "total_appointments": summary_controller.total_appointments(),
        "total_revenue": summary_controller.total_revenue(),
        "average_service_rating": summary_controller.avarage_service_rating(),
        "average_aesthetician_rating": summary_controller.avarage_aesthetician_rating(),
        "average_branch_rating": summary_controller.avarage_branch_rating(),
        "total_service": summary_controller.total_services(),
        "total_branches": summary_controller.total_branches(),
        "total_aestheticians": summary_controller.total_aestheticians(),
        "total_active_vouchers": summary_controller.total_active_vouchers(),
        "sex-count-by-aesthetician": summary_controller.sex_count_by_aesthetician(),
    })




# appointments
@analytics_bp.route(rule="/appointments", methods=["GET"])
def get_appointment_analytics():
    return jsonify({
        "appointments_overtime": appointment_analytics_controller.appointment_overtime(),
        "appointments_by_service_category": appointment_analytics_controller.appointments_by_service_category(),
        "appointments_by_service": appointment_analytics_controller.appointments_by_service(),
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
        "payment_popularity": sales_analytics_controller.payment_popularity()
    })
