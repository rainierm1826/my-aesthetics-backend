from flask import jsonify
from sqlalchemy import func, desc, extract
from ..models.appointment_model import Appointment
from ..models.service_model import Service
from ..models.branch_model import Branch
from ..models.aesthetician_model import Aesthetician
from ..extension import db


class AnalyticsController:
    def __init__(self, request):
        self.request = request
        self.model = Appointment

    def _apply_filter(self, query, model):
        branch = self.request.args.get("branch")
        year = self.request.args.get("year", type=int)

        if branch:
            query = query.join(Branch).filter(Branch.branch_name == branch)
        if year:
            query = query.filter(extract("year", model.created_at) == year)

        return query

    def _base_query(self):
        return self._apply_filter(db.session.query(self.model), self.model)

    def _apply_grouping(self, query, date_column, aggregate_func, label):
        group_by = self.request.args.get("group-by", "monthly")

        if group_by == "weekly":
            label_expr = func.to_char(date_column, 'Day')  # Monday, Tuesday
        elif group_by == "monthly":
            label_expr = func.to_char(date_column, 'Month')  # January
        elif group_by == "yearly":
            label_expr = func.to_char(date_column, 'YYYY')  # 2024
        else:
            label_expr = func.to_char(date_column, 'Month')  # Default: monthly

        results = query.with_entities(
            label_expr.label("label"),
            aggregate_func.label(label)
        ).group_by(label_expr).order_by(label_expr).all()

        # Convert Row objects to dicts with cleaned labels
        return [
            {"label": row.label.strip(), label: float(getattr(row, label) or 0.0)}
            for row in results
        ]

    def total_appointment(self):
        query = self._base_query()
        return jsonify(self._apply_grouping(query, self.model.created_at, func.count(), label="count"))

    def overall_earnings(self):
        query = self._base_query()
        return jsonify(self._apply_grouping(query, self.model.created_at, func.sum(self.model.to_pay), label="total"))

    def earnings_per_service(self):
        query = self._base_query().join(Service, self.model.service_id == Service.service_id)

        results = query.with_entities(
            Service.service_name,
            func.sum(self.model.to_pay).label("earnings")
        ).group_by(Service.service_name).order_by(Service.service_name).all()

        return jsonify([
            {"service_name": service_name.strip(), "earnings": float(earnings or 0.0)}
            for service_name, earnings in results
        ])

    def service_popularity(self):
        query = self._base_query().join(Service, self.model.service_id == Service.service_id)

        results = query.with_entities(
            Service.service_name,
            func.count().label("count")
        ).group_by(Service.service_name).order_by(Service.service_name).all()

        return jsonify([
            {"service_name": name.strip(), "count": count} for name, count in results
        ])

    def appointment_status_summary(self):
        results = self._base_query().with_entities(
            self.model.status,
            func.count().label("count")
        ).group_by(self.model.status).order_by(self.model.status).all()

        return jsonify([
            {"status": status, "count": count} for status, count in results
        ])



    def peak_booking_analysis(self):
        query = self._base_query()

        group_by = self.request.args.get("group-by")

        if group_by == "weekly":
            results = query.with_entities(
                func.to_char(self.model.created_at, 'Day').label("day"),
                func.count().label("count")
            ).group_by("day").order_by("day").all()

            return jsonify([
                {"day": row.day.strip(), "count": row.count}
                for row in results
            ])


    def top_rated_aesthetician(self):
        results = self._base_query().with_entities(
            self.model.aesthetician_id,
            func.avg(self.model.aesthetician_rating).label("rating")
        ).group_by(self.model.aesthetician_id).order_by(desc("rating")).limit(10).all()

        return jsonify([
            {"aesthetician_id": aid, "avg_rating": round(rating or 0.0, 2)} for aid, rating in results
        ])

    def top_rated_branch(self):
        results = self._base_query().with_entities(
            self.model.branch_id,
            func.avg(self.model.branch_rating).label("rating")
        ).group_by(self.model.branch_id).order_by(desc("rating")).limit(10).all()

        return jsonify([
            {"branch_id": bid, "avg_rating": round(rating or 0.0, 2)} for bid, rating in results
        ])

    def top_rated_service(self):
        results = self._base_query().with_entities(
            self.model.service_id,
            func.avg(self.model.service_rating).label("rating")
        ).group_by(self.model.service_id).order_by(desc("rating")).limit(10).all()

        return jsonify([
            {"service_id": sid, "avg_rating": round(rating or 0.0, 2)} for sid, rating in results
        ])
