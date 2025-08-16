from ..controllers.analytics_controller import AnalyticsController
from flask import Blueprint, request

analytics_bp = Blueprint("analytics", __name__)
analytics_controller = AnalyticsController(request=request)

@analytics_bp.route(rule="/total-appointment", methods=["GET"])
def get_total_appointments():
    return analytics_controller.total_appointment()


@analytics_bp.route(rule="/service-popularity", methods=["GET"])
def get_service_popularity():
    return analytics_controller.service_popularity()


@analytics_bp.route(rule="/appointment-status-summary", methods=["GET"])
def get_appointment_status_summary():
    return analytics_controller.appointment_status_summary()


@analytics_bp.route(rule="/overall-earnings", methods=["GET"])
def get_overall_earnings():
    return analytics_controller.overall_earnings()


@analytics_bp.route(rule="/earnings-per-service", methods=["GET"])
def get_earnings_per_service():
    return analytics_controller.earnings_per_service()


@analytics_bp.route(rule="/peak-booking-analysis", methods=["GET"])
def get_peak_booking_analysis():
    return analytics_controller.peak_booking_analysis()