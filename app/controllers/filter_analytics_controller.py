from ..models.appointment_model import Appointment
from sqlalchemy import extract
from flask import request

class FilterAnalyticsController:
    
    @staticmethod
    def get_filter_params():
        return {
            'month': request.args.get("month", type=int),
            'year': request.args.get("year", type=int),
            'branch_id': request.args.get("branch", type=str)
        }
    
    @staticmethod
    def apply_filter_date(query, month=None, year=None):
        if year:
            query = query.filter(extract("year", Appointment.created_at) == year)
        if month:
            query = query.filter(extract("month", Appointment.created_at) == month)
        return query
    
    @staticmethod
    def apply_filter_branch(query, branch_id=None):
        if branch_id:
            query = query.filter(Appointment.branch_id == branch_id)
        return query
    
    @staticmethod
    def apply_all_filters(query, month=None, year=None, branch_id=None):
        query = FilterAnalyticsController.apply_filter_branch(query, branch_id)
        query = FilterAnalyticsController.apply_filter_date(query, month, year)
        return query
    
    @staticmethod
    def apply_filters_from_request(query):
        params = FilterAnalyticsController.get_filter_params()
        return FilterAnalyticsController.apply_all_filters(
            query, 
            params['month'], 
            params['year'], 
            params['branch_id']
        )
        
            
    
        