from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify, request
from ..controllers.analytics_summary_controller import AnalyticsSummaryController


def access_control(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            if user_role not in roles:
                return jsonify({"status": False, "message": f"Unauthorized. User role: {user_role}, Required: {roles}"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def with_analytics_controller(controller_cls):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            month = request.args.get("month", type=int)
            year = request.args.get("year", type=int)
            branch_id = request.args.get("branch_id", type=str)

            controller = controller_cls(month=month, year=year, branch_id=branch_id)
            return f(controller, *args, **kwargs)
        return decorated_function
    return decorator
    
                
