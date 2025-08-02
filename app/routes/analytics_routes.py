# from flask import Blueprint, request, jsonify
# from ..helper.functions import total_sales_service, total_sales_aesthetician, total_sales_overtime, count_appointment_overtime, service_popularity, count_status_overtime
# import calendar

# analytics_bp = Blueprint("analytics", __name__)

# @analytics_bp.route("/get-sales", methods=["GET"])
# def get_sales_overtime():
#     try:
#         group_by = request.args.get("group_by", "month")
#         year = request.args.get("year", type=int)
#         month = request.args.get("month", type=int)
#         branch = request.args.get("branch")
        
#         sales_data = total_sales_overtime(group_by=group_by, year=year, month=month, branch=branch)
        
#         result = [
#             {
#                 group_by: calendar.month_name[int(row[0])] if group_by == "month" else int(row[0]),
#                 "total": float(row[1])
#             }
#             for row in sales_data
#         ]
        
#         return jsonify({"status": True, "message": "Sales data fetched", "sales": result}), 200
        
#     except Exception as e:
#         return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

# @analytics_bp.route("/get-appointment-count", methods=["GET"])
# def get_count_appointment_overtime():
#     try:
#         group_by = request.args.get("group_by", "month")
#         year = request.args.get("year", type=int)
#         month = request.args.get("month", type=int)
#         branch = request.args.get("branch")
        
#         count_data = count_appointment_overtime(group_by=group_by, year=year, month=month, branch=branch)
        
#         result = [
#             {
#                 group_by: calendar.month_name[int(row[0])] if group_by == "month" else int(row[0]),
#                 "appointment_count": int(row[1])
#             }
#             for row in count_data
#         ]
        
#         return jsonify({"status": True, "data": result}), 200
        
#     except Exception as e:
#         return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

# @analytics_bp.route("/get-status-count", methods=["GET"])
# def get_count_status_overtime():
#     try:
#         year = request.args.get("year", type=int)
#         month = request.args.get("month", type=int)
#         branch = request.args.get("branch")
        
#         count_data = count_status_overtime(group_by="status", year=year, month=month, branch=branch)
        
#         result = [
#             {
#                 "status": status,
#                 "status_count": int(status_count)
#             }
#             for status, status_count in count_data
#         ]
        
#         return jsonify({"status": True, "data": result}), 200
        
#     except Exception as e:
#         return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    
# @analytics_bp.route("/get-service-popularity", methods=["GET"])
# def get_service_popularity_overtime():
#     try:
#         year = request.args.get("year", type=int)
#         month = request.args.get("month", type=int)
#         branch = request.args.get("branch")
        
#         count_data = service_popularity(year=year, month=month, branch=branch)
        
#         result = [
#             {
#                 "service": service,
#                 "data": int(popularity_count)
#             }
#             for service, popularity_count in count_data
#         ]
        
#         return jsonify({"status": True, "data": result}), 200
        
#     except Exception as e:
#         return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

# @analytics_bp.route("/get-service-report", methods=["GET"])
# def get_service_report():
#     try:
#         year = request.args.get("year", type=int)
#         month = request.args.get("month", type=int)
#         branch = request.args.get("branch")
#         service_report = total_sales_service(group_by="service", year=year, month=month, branch=branch)

#         result = [
#             {
#                 "service": service_name,
#                 "total_earnings": float(total)
#             }
#             for service_name, total in service_report
#         ]
        
#         return jsonify({"service": result})

#     except Exception as e:
#         return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    
# @analytics_bp.route("/get-category-report", methods=["GET"])
# def get_category_report():
#     try:
#         year = request.args.get("year", type=int)
#         month = request.args.get("month", type=int)
#         branch = request.args.get("branch")
#         category_report = total_sales_service(group_by="category", year=year, month=month, branch=branch)

#         result = [
#             {
#                 "category": category,
#                 "total_earnings": float(total)
#             }
#             for category, total in category_report
#         ]
        
#         return jsonify({"service": result})

#     except Exception as e:
#         return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    
# @analytics_bp.route("/get-aesthetician-report", methods=["GET"])
# def get_aesthetician_report():
#     try:
#         year = request.args.get("year", type=int)
#         month = request.args.get("month", type=int)
#         branch = request.args.get("branch")
#         aesthetician_sales_report = total_sales_aesthetician(group_by="aesthetician", year=year, month=month, branch=branch, limit=12)

#         result = [
#             {
#                 "aesthetician": aesthetician,
#                 "total": float(total)
#             }
#             for aesthetician, total in aesthetician_sales_report
#         ]
        
#         return jsonify({"aesthetician": result})

#     except Exception as e:
#         return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500