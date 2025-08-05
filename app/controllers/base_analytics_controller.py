from sqlalchemy import func
from ..models.appointment_model import Appointment
from ..models.branch_model import Branch
from ..models.service_model import Service
from ..models.aesthetician_model import Aesthetician
from ..extension import db


class BaseAnalyticsController:
    def __init__(self, model, group_column):
        self.model = model
        self.group_column = group_column
           
    def _apply_filter(self, query, branch=None, year=None, month=None):
        if year:
            query = query.filter(func.extract("year", Appointment.created_at) == year)

        if month:
            query = query.filter(func.extract("month", Appointment.created_at) == month)
        
        if branch:
            query = query.filter(Branch.branch_name.ilike(f"%{branch}%"))
        return query
    

    def _base_query(self, join=None, filter=None):
        query = db.session.query()
        query = query.select_from(Appointment)
        
        default_joins = [
            (Service, Appointment.service_id == Service.service_id),
            (Branch, Appointment.branch_id == Branch.branch_id),
            (Aesthetician, Appointment.aesthetician_id == Aesthetician.aesthetician_id),
        ]        
        if join:
            default_joins.extend(join)
        for join_table, join_condition in default_joins:
            query = query.join(join_table, join_condition)  
        if filter is None:
            filter = []    
        for filter_condition in filter:
            query = query.filter(filter_condition)
        
        return query
    
    def _aggregate_query(
        self,
        aggregate_field=None,
        aggregate_func=None,
        group_by=None,
        additional_joins=None,
        branch=None,
        year=None,
        month=None,
        limit=None,
        filter=None
    ):
        query = self._base_query(join=additional_joins, filter=filter)
        query = self._apply_filter(query, branch, year, month)

        if aggregate_func and aggregate_field:
            if group_by:
                group_field = self.group_column[group_by]
                query = query.with_entities(
                    group_field.label(group_by),
                    aggregate_func(aggregate_field).label("total")
                ).group_by(group_field).order_by(group_field)
            else:
                query = query.with_entities(
                    aggregate_func(aggregate_field).label("total")
                )
        else:
            if group_by:
                group_field = self.group_column[group_by]
                query = query.with_entities(group_field.label(group_by)).distinct()
            else:
                query = query.with_entities(Appointment)

        if limit:
            query = query.limit(limit)

        return query.all()

    
    