from .base_crud_controller import BaseCRUDController
from ..models.service_model import Service
from ..models.branch_model import Branch
from flask import jsonify, request
from ..extension import db
from sqlalchemy import or_

class ServiceController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Service,
            id_field="service_id",
            required_fields=["service_name", "price", "is_sale", "category", "duration"],
            searchable_fields=["service_name"],
            filterable_fields={"category": "category", "branch": (Branch, "branch_id")},
            updatable_fields=["service_name", "branch_id", "discount", "is_sale", "discount_type", "category", "image", "description", "price", "duration"],
            sortable_fields={"price": Service.price, "service": Service.service_name, "rate": Service.average_rate},
            joins=[(Branch, Service.branch_id == Branch.branch_id, "left")],
    
        )
    
    def get_service_name(self):
        try:
            branch = request.args.get("branch")
            
            query = (
                db.session.query(
                    Service.service_id,
                    Service.service_name,
                    Service.price,
                    Service.discounted_price,
                    Service.discount_type,
                    Service.discount,
                    Service.duration
                ).filter_by(isDeleted=False)
            )
            if branch and branch.lower() != "all":
                query = query.filter(
                    or_(Service.branch_id == branch, Service.branch_id == None)
                )
            
            result = query.all()

            services = [
                {
                    "service_id": a.service_id,
                    "service_name":a.service_name,
                    "price":a.price,
                    "discounte_type":a.discount_type,
                    "discount":a.discount,
                    "discounted_price":a.discounted_price,
                    "duration": a.duration
                }
                for a in result
            ]

            return jsonify({"status": True, "message": "Retrieved successfully", "service": services})
        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)})
    
    def _apply_filters(self, query):
        # Category filter works normally
        category = request.args.get("category")
        if category:
            query = query.filter(Service.category == category)

        # Branch filter: include services for that branch OR global (NULL)
        branch = request.args.get("branch")
        if branch and branch.lower() != "all":
            query = query.filter(
                or_(Service.branch_id == branch, Service.branch_id == None)
            )

        return query

    
    def _custom_create(self, data):

        data["price"] = float(request.form.get("price"))
        data['is_sale'] = request.form.get("is_sale", str(data.get('is_sale', False))) == "true"
        data["discount"] = float(request.form.get("discount"))

        # Interpret 'all' or empty branch as global (None)
        if data.get('branch_id') in ('all', '', None):
            data['branch_id'] = None
        
        new_service = Service(**data)
        
        db.session.add(new_service)
        return new_service

    def _custom_update(self, data):
        service = Service.query.get(data.get('service_id'))
        if not service:
            return jsonify({"status": False, "message": "service not found"}), 404

        # Map form values
        price_raw = request.form.get('price')
        if price_raw is not None:
            try:
                service.price = float(price_raw)
            except ValueError:
                pass

        discount_raw = request.form.get('discount')
        if discount_raw is not None:
            try:
                service.discount = float(discount_raw)
            except ValueError:
                pass

        is_sale_raw = request.form.get('is_sale')
        if is_sale_raw is not None:
            service.is_sale = is_sale_raw == 'true'

        # Branch handling: 'all' or empty -> global (None)
        branch_val = request.form.get('branch_id')
        if branch_val is not None:
            if branch_val in ('all', ''):
                service.branch_id = None
                # Ensure subsequent generic update loop doesn't reapply 'all'
                data['branch_id'] = None
            else:
                service.branch_id = branch_val
                data['branch_id'] = branch_val

        # Other simple fields
        for field in ['service_name', 'category', 'description', 'discount_type', 'duration', 'image']:
            raw = request.form.get(field)
            if raw is not None and raw != '':
                if field == 'duration':
                    try:
                        service.duration = int(raw)
                    except ValueError:
                        pass
                else:
                    setattr(service, field, raw)

        # Recalculate discounted_price if discount present
        if service.discount is not None and service.price is not None:
            if service.discount_type == 'percentage':
                service.discounted_price = max(0, service.price - (service.price * service.discount / 100.0))
            elif service.discount_type == 'fixed':
                service.discounted_price = max(0, service.price - service.discount)
        else:
            service.discounted_price = service.price

        db.session.commit()
        return service
    
        
        
    
