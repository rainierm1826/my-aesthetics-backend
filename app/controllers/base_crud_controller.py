from flask import request, jsonify
from ..extension import db
from sqlalchemy import or_, asc, desc
from ..helper.functions import validate_required_fields

class BaseCRUDController:
    def __init__(self, model, id_field, required_fields=None, searchable_fields=None, filterable_fields=None, updatable_fields=None, sortable_fields=None, joins=None):
        self.model = model
        self.id_field = id_field
        self.required_fields = required_fields or []
        self.searchable_fields = searchable_fields or []
        self.filterable_fields = filterable_fields or {}
        self.updatable_fields = updatable_fields or []
        self.sortable_fields = sortable_fields or {}
        self.resource_name = model.__tablename__
        self.joins = joins or []
    
    # public methods for CRUD operations
    def create(self):
        try:
            data = request.json
            # check if the required fields are present
            if not validate_required_fields(data, self.required_fields):
                return jsonify({"status": False, "message": "missing required fields"}), 400
            
            if hasattr(self, "_custom_create"):
                new_instance = self._custom_create(data)
                # If the custom create returns a tuple (e.g., (response, status)), return it directly
                if isinstance(new_instance, tuple):
                    return new_instance
            else:
                new_instance = self.model(**data)
                db.session.add(new_instance)
            db.session.commit()
            return jsonify({
                "status": True,
                "message": f"{self.resource_name} created successfully",
                self.resource_name: new_instance.to_dict()
            }), 201
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500
    
    # generic get all method 
    def get_all(self):
        try:
            query = self.model.query
            
            query = self._apply_joins(query)
            
            query = self._apply_search(query)
            
            query = self._apply_filters(query)
            
            query = self._apply_sorting(query)
            
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 12))
            
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            items = [item.to_dict() for item in pagination.items]
            
            return jsonify({
                "status": True,
                "message": f"{self.resource_name} retrieved successfully",
                self.resource_name: items,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500
    
    # generic update method
    def update(self):
        try:
            data = request.json
            
            if hasattr(self, "_custom_update"):
                updated_instance = self._custom_update(data)

                if isinstance(updated_instance, tuple):
                    return updated_instance
                elif updated_instance is not None:
                    # If custom update returns an instance, use it
                    instance = updated_instance
                else:
                    # If custom update returns None, get instance normally
                    instance = self.model.query.filter(getattr(self.model, self.id_field) == data[self.id_field]).first()
            else:
                # No custom update method, get instance normally
                instance = self.model.query.filter(getattr(self.model, self.id_field) == data[self.id_field]).first()
            
            if not instance:
                return jsonify({
                    "status": False,
                    "message": f"{self.resource_name} not found"
                }), 404
            
            # Update the fields
            for field in self.updatable_fields:
                if field in data:
                    setattr(instance, field, data[field])
            
            db.session.commit()
            return jsonify({
                "status": True,
                "message": f"{self.resource_name} updated successfully",
                self.resource_name: instance.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500
        
    # generic delete method
    def delete(self):
        try:
            data = request.json
            
            if self.id_field not in data:
                return jsonify({
                "status": False,
                "message": f"missing {self.resource_name} id"
            }), 404
            
            instance = self.model.query.filter(getattr(self.model, self.id_field) == data[self.id_field]).first()
            
            if not instance:
                return jsonify({
                "status": False,
                "message": f"{self.resource_name} not found"
            }), 404
            
            db.session.delete(instance)
            db.session.commit()
            
            return jsonify({
                "status": True,
                "message": f"{self.resource_name} deleted successfully"
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500 
    
    # get the details of the resource by id
    def get_by_id(self, id):
        try:
            instance = self.model.query.filter(getattr(self.model, self.id_field) == id).first()
            if not instance:
                return jsonify({
                    "status": False,
                    "message": f"{self.resource_name} not found"
                }), 404
            
            return jsonify({
                "status": True,
                "message": f"{self.resource_name} retrieved successfully",
                self.resource_name: instance.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500
    
    
    
    # private methods
    def _apply_search(self, query):
        search = request.args.get("search")
        if search and self.searchable_fields:
            search_conditions = []
            for field in self.filterable_fields:
                search_conditions.append(getattr(self.model, field).ilike(f"%{search}%"))
            query = query.filter(or_(search_conditions))
        return query
    
    def _apply_filters(self, query):
        for param, model_field in self.filterable_fields.items():
            value = request.args.get(param)
            if value:
                if isinstance(model_field, tuple):
                    model, field = model_field
                    query = query.filter(getattr(model, field)==value)
                else:
                    query = query.filter(getattr(self.model, model_field)==value)
        return query
        
    def _apply_sorting(self, query):
        sort = request.args.get("sort")
        if sort:
            field_name, direction = sort.split(":")
            column = self.sortable_fields.get(field_name)
            if column:
                if direction == "asc":
                    query = query.order_by(asc(column))
                if direction == "desc":
                    query = query.order_by(desc(column))
        return query
            
    def _apply_joins(self, query):
        for join_item in self.joins:
            if len(join_item) == 2:
                model, condition = join_item
                query = query.join(model, condition)
            elif len(join_item) == 3:
                model, condition, join_type = join_item
                if join_type == "left":
                    query = query.outerjoin(model, condition)
                else:
                    query = query.join(model, condition)
        return query