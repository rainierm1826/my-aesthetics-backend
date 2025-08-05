from .base_analytics_controller import BaseAnalyticsController
from ..models.appointment_model import Appointment
from ..models.aesthetician_model import Aesthetician
from ..models.service_model import Service
from ..models.branch_model import Branch
from sqlalchemy import func
from flask import jsonify

class AnalyticsController(BaseAnalyticsController):
    
    def __init__(self):
        group_column = {
            "branch": Branch.branch_name,
            "service": Service.service_name,
            "aesthetician": Aesthetician.first_name,
            "status": Appointment.status
        }
        super().__init__(Appointment, group_column)
    
    def get_total_sales(self, aggregate_field, group_by=None, branch=None, year=None, month=None, filter=None):
        total_sales = self._aggregate_query(
            group_by=group_by,
            aggregate_field=aggregate_field,
            filter=filter,
            aggregate_func=func.sum,
            branch=branch,
            year=year,
            limit=10,
            month=month)
        
        if group_by:
            result = [
                {
                    group_by: row[0],
                    "total": float(row[1])
                }
                for row in total_sales
            ]
        else:
            result = float(total_sales[0][0]) if total_sales else 0.0
                
        return jsonify(result)
        
    
    def count_field(self, aggregate_field, group_by=None, branch=None, year=None, month=None, filter=None):
        count = self._aggregate_query(
            group_by=group_by,
            filter=filter,
            aggregate_field=aggregate_field,
            aggregate_func=func.count,
            branch=branch,
            year=year,
            limit=10,
            month=month)
        
        if group_by:
            result = [
                {
                    group_by: row[0],
                    "count": float(row[1])
                }
                for row in count
            ]
        else:
            result = {"count": float(count[0][0]) if count else 0.0}
                
        return jsonify(result)