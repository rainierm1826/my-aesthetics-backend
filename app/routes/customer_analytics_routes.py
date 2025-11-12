from flask import Blueprint, jsonify
from ..controllers.customer_analytics_controller import CustomerAnalyticsController
from flask_jwt_extended import jwt_required
from ..helper.decorators import access_control

customer_analytics_bp = Blueprint('customer_analytics', __name__)

controller = CustomerAnalyticsController()

@customer_analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
@access_control("owner")
def customer_summary():
    return jsonify({
        "total_customers": controller.total_customers(),
        "active_customers": controller.active_customers(days=30),
        "customer_retention_rate": controller.customer_retention_rate(),
        "average_customer_lifetime_value": controller.average_customer_lifetime_value()
    })

@customer_analytics_bp.route('/detail', methods=['GET'])
@jwt_required()
def customer_detail():
    return controller.customer_detail()

@customer_analytics_bp.route('/timeline', methods=['GET'])
@jwt_required()
def customer_timeline():
    return controller.customer_appointments_timeline()

@customer_analytics_bp.route('/spending-by-service', methods=['GET'])
@jwt_required()
def spending_by_service():
    return controller.customer_spending_by_service()
