from flask import Blueprint
from ..controllers.customer_analytics_controller import CustomerAnalyticsController
from flask_jwt_extended import jwt_required

customer_analytics_bp = Blueprint('customer_analytics', __name__)

controller = CustomerAnalyticsController()

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
