from sqlalchemy import extract
from flask import request

class BasicFilterAnalyticsController:
    
    @staticmethod
    def get_filter_params():
        return {
            'month': request.args.get("month", type=int),
            'year': request.args.get("year", type=int),
            'branch_id': request.args.get("branch", type=str)
        }

    @staticmethod
    def apply_not_deleted(query, model):
        """Apply isDeleted = false if model has that attribute"""
        if hasattr(model, "isDeleted"):
            query = query.filter(model.isDeleted == False)
        return query
    
    @staticmethod
    def apply_filter_date(query, model, month=None, year=None):
        """Apply date filtering if model has created_at field"""
        if hasattr(model, "created_at"):
            if year:
                query = query.filter(extract("year", model.created_at) == year)
            if month:
                query = query.filter(extract("month", model.created_at) == month)
        return query
    
    @staticmethod
    def apply_filter_branch(query, model, branch_id=None):
        """Apply branch filtering if model has branch_id field"""
        if branch_id and hasattr(model, "branch_id"):
            query = query.filter(model.branch_id == branch_id)
        return query
    
    @staticmethod
    def apply_basic_filters(query, model, month=None, year=None, branch_id=None):
        """Apply all basic filters (no appointment-specific filters)"""
        query = BasicFilterAnalyticsController.apply_not_deleted(query, model)
        query = BasicFilterAnalyticsController.apply_filter_branch(query, model, branch_id)
        query = BasicFilterAnalyticsController.apply_filter_date(query, model, month, year)
        return query
    
    @staticmethod
    def apply_filters_from_request(query, model):
        """Apply filters from request parameters"""
        params = BasicFilterAnalyticsController.get_filter_params()
        return BasicFilterAnalyticsController.apply_basic_filters(
            query,
            model,
            params['month'], 
            params['year'], 
            params['branch_id']
        )