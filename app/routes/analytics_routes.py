from ..models.appointment_model import Appointment
from ..models.service_model import Service
from flask import Blueprint, request, jsonify
from ..helper.functions import filter_sales
import calendar

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/get-sales", methods=["GET"])
def get_sales():
    try:
        group_by = request.args.get("group_by", "month")
        year = request.args.get("year", type=int)
        month = request.args.get("month", type=int)
        
        sales_data = filter_sales(group_by=group_by, year=year, month=month)
        
        result = [
            {
                group_by: calendar.month_name[int(row[0])] if group_by == "month" else int(row[0]),
                "total": float(row[1])
            }
            for row in sales_data
        ]
        
        return jsonify({"status": True, "message": "Sales data fetched", "sales": result}), 200
        
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500 