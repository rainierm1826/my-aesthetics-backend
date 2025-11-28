from flask import request, jsonify
from ..extension import db
from sqlalchemy import or_, asc, desc, func
from ..helper.functions import validate_required_fields, convert_formdata_types
import cloudinary.uploader

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
            if request.is_json:
                data = request.get_json()
                image = None
            else:
                data = request.form.to_dict()
                image = request.files.get("image")
            
            data = convert_formdata_types(data)
          
            # Check required fields first
            if not validate_required_fields(data, self.required_fields):
                return jsonify({"status": False, "message": "missing required fields"}), 400
            
            # Create the instance without the image
            if hasattr(self, "_custom_create"):
                new_instance = self._custom_create(data)
                if isinstance(new_instance, tuple):
                    return new_instance
            else:
                new_instance = self.model(**data)
                db.session.add(new_instance)
            
            # Commit first
            db.session.commit()
            
            # Upload image after commit
            if image:
                upload_result = cloudinary.uploader.upload(image)
                new_instance.image = upload_result["secure_url"]
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
            print(e)
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
            
            if hasattr(self.model, "isDeleted"):
                query = query.filter(self.model.isDeleted == False)
            
            query = self._apply_joins(query)
            
            query = self._apply_search(query)
            
            query = self._apply_filters(query)
            
            query = self._apply_sorting(query)
            
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("limit", 12))
            
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
            print(str(e))
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500
    
    # generic update method
    def update(self):
        try:
            # Use form-data only
            if request.is_json:
                data = request.get_json()
                image = None
            else:
                data = request.form.to_dict()
                image = request.files.get("image")
            
            data=convert_formdata_types(data)
            print(data)
                        
            if hasattr(self, "_custom_update"):
                new_instance = self._custom_update(data)
                if isinstance(new_instance, tuple):
                    return new_instance

            # Get the instance
            instance = self.model.query.filter(
                getattr(self.model, self.id_field) == data[self.id_field]
            ).first()

            if not instance:
                return jsonify({"status": False, "message": f"{self.resource_name} not found"}), 404

            # Update other allowed fields
            for field in self.updatable_fields:
                if field in data:
                    setattr(instance, field, data[field])

            # Update image if uploaded
            if image:
                upload_result = cloudinary.uploader.upload(image)
                instance.image = upload_result["secure_url"]

            db.session.commit()

            return jsonify({
                "status": True,
                "message": f"{self.resource_name} updated successfully",
                self.resource_name: instance.to_dict()
            }), 200

        except Exception as e:
            db.session.rollback()
            print(e)
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500

    # generic soft delete method
    def delete(self, id):
        try:
            
            instance = (
                self.model.query
                .filter(getattr(self.model, self.id_field) == id)
                .first()
            )
            
            if not instance:
                return jsonify({
                    "status": False,
                    "message": f"{self.resource_name} not found"
                }), 404
            
            if hasattr(instance, "isDeleted"):
                instance.isDeleted = True
                db.session.commit()
            else:
                db.session.delete(instance)
                db.session.commit()
            
            return jsonify({
                "status": True,
                "message": f"{self.resource_name} deleted successfully"
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500

    
    
    def get_by_id(self, id):
        try:
            instance = self.model.query.filter(getattr(self.model, self.id_field) == id).filter_by(isDeleted=False).first()
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
        search = request.args.get("query")
        if search and self.searchable_fields:
            search_conditions = [
                getattr(self.model, field).ilike(f"%{search}%")
                for field in self.searchable_fields
                if hasattr(self.model, field) 
            ]
            
            # Add full name search if first_name, last_name, and middle_initial exist
            if (hasattr(self.model, 'first_name') and 
                hasattr(self.model, 'last_name') and 
                hasattr(self.model, 'middle_initial')):
                full_name_with_mi = func.concat(
                    self.model.first_name, ' ',
                    self.model.middle_initial, '. ',
                    self.model.last_name
                )
                full_name_without_mi = func.concat(
                    self.model.first_name, ' ',
                    self.model.last_name
                )
                search_conditions.extend([
                    full_name_with_mi.ilike(f"%{search}%"),
                    full_name_without_mi.ilike(f"%{search}%")
                ])
            
            if search_conditions: 
                query = query.filter(or_(*search_conditions))
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
            if column is not None:
                if direction == "asc":
                    query = query.order_by(asc(column).nullslast())
                elif direction == "desc":
                    query = query.order_by(desc(column).nullslast())
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