from ..controllers.base_crud_controller import BaseCRUDController
from ..models.user_model import User
from ..models.owner_model import Owner
from ..models.admin_model import Admin
from ..models.walk_in_model import WalkIn
from ..models.auth_model import Auth
from flask_jwt_extended import get_jwt_identity, get_jwt
from flask import jsonify, request
from ..extension import db
from datetime import datetime
import cloudinary.uploader


class UserController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=User,
            id_field="user_id",
            updatable_fields=["first_name", "last_name", "middle_initial", "phone_number", "birthday", "image"]
        )

    def get_by_id(self):
        identity = get_jwt_identity()
        role = get_jwt().get("role")

        model_map = {
            "customer": User,
            "admin": Admin, 
            "owner": Owner
        }
        
        model = model_map.get(role)
        if not model:
            return jsonify({"status": False, "message": "Invalid role"}), 400

        try:
            user = model.query.filter(model.account_id == identity).first()
            
            if not user:
                return jsonify({"status": False, "message": "user not found"}), 404
            
            return jsonify({
                "status": True,
                "message": "user retrieved successfully",
                "user": user.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return jsonify({
                "status": False,
                "message": "internal error",
                "error": str(e)
            }), 500

    
    
    # update your own account
    def update(self):
        identity = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")
        
        # Get the appropriate model and user
        if role == "customer":
            user = User.query.filter_by(account_id=identity).first()
        elif role == "admin":
            user = Admin.query.filter_by(account_id=identity).first()
        elif role == "owner":
            user = Owner.query.filter_by(account_id=identity).first()
        else:
            return jsonify({"status": False, "message": "Invalid role"}), 400

        
        if not user:
            return jsonify({"status": False, "message": "user not found"}), 404
        
        try:
            data = request.form.to_dict()
            image = request.files.get("image")
            if image:
                upload_result = cloudinary.uploader.upload(image)
                data["image"] = upload_result["secure_url"]
                
            # Update only the allowed fields
            for field in self.updatable_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            db.session.commit()
            
            return jsonify({
                "status": True,
                "message": "user updated successfully",
                "user": user.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return jsonify({
                "status": False,
                "message": "internal error", 
                "error": str(e)
            }), 500
    
    def get_all_customers(self):
        try:
            # Get query parameters for pagination and filtering
            page = request.args.get("page", 1, type=int)
            limit = request.args.get("limit", 10, type=int)
            search = request.args.get("search", "", type=str)
            customer_type = request.args.get("type", "", type=str)  # "online", "walkin", or empty for all
            sort_by = request.args.get("sort_by", "created_at", type=str)
            order = request.args.get("order", "desc", type=str)  # "asc" or "desc"
            
            from sqlalchemy import func
            
            # Build online customers query - only fetch customers with role_id = "1"
            online_query = User.query.join(Auth, User.account_id == Auth.account_id).filter(
                User.isDeleted == False,
                Auth.role_id == "1"  # Only customers, not admin or owner
            )
            
            # Build walk-in customers query
            walkin_query = WalkIn.query.filter(WalkIn.isDeleted == False)
            
            # Apply search filter
            if search:
                # Create full name search conditions for online customers
                online_full_name_with_mi = func.concat(
                    User.first_name, ' ',
                    User.middle_initial, '. ',
                    User.last_name
                )
                online_full_name_without_mi = func.concat(
                    User.first_name, ' ',
                    User.last_name
                )
                
                online_query = online_query.filter(
                    db.or_(
                        User.first_name.ilike(f"%{search}%"),
                        User.last_name.ilike(f"%{search}%"),
                        User.phone_number.ilike(f"%{search}%"),
                        online_full_name_with_mi.ilike(f"%{search}%"),
                        online_full_name_without_mi.ilike(f"%{search}%")
                    )
                )
                
                # Create full name search conditions for walk-in customers
                walkin_full_name_with_mi = func.concat(
                    WalkIn.first_name, ' ',
                    WalkIn.middle_initial, '. ',
                    WalkIn.last_name
                )
                walkin_full_name_without_mi = func.concat(
                    WalkIn.first_name, ' ',
                    WalkIn.last_name
                )
                
                walkin_query = walkin_query.filter(
                    db.or_(
                        WalkIn.first_name.ilike(f"%{search}%"),
                        WalkIn.last_name.ilike(f"%{search}%"),
                        WalkIn.phone_number.ilike(f"%{search}%"),
                        walkin_full_name_with_mi.ilike(f"%{search}%"),
                        walkin_full_name_without_mi.ilike(f"%{search}%")
                    )
                )
            
            # Filter by customer type
            if customer_type == "online":
                walkin_query = None
            elif customer_type == "walkin":
                online_query = None
            
            # Get counts before pagination
            online_count = online_query.count() if online_query else 0
            walkin_count = walkin_query.count() if walkin_query else 0
            total_count = online_count + walkin_count
            
            # Determine sort field and order
            if sort_by == "name":
                sort_field_online = User.first_name
                sort_field_walkin = WalkIn.first_name
            elif sort_by == "phone":
                sort_field_online = User.phone_number
                sort_field_walkin = WalkIn.phone_number
            else:  # created_at (default)
                sort_field_online = User.created_at
                sort_field_walkin = WalkIn.created_at
            
            is_descending = order.lower() == "desc"
            
            # Apply sorting (without pagination yet)
            if online_query:
                if is_descending:
                    online_query = online_query.order_by(sort_field_online.desc())
                else:
                    online_query = online_query.order_by(sort_field_online.asc())
            
            if walkin_query:
                if is_descending:
                    walkin_query = walkin_query.order_by(sort_field_walkin.desc())
                else:
                    walkin_query = walkin_query.order_by(sort_field_walkin.asc())
            
            # Fetch all data (we'll paginate after merging)
            online_customers = online_query.all() if online_query else []
            walkin_customers = walkin_query.all() if walkin_query else []
            
            # Format all customers into a single list
            all_customers = []
            
            for customer in online_customers:
                all_customers.append({
                    "id": customer.user_id,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "middle_initial": customer.middle_initial,
                    "phone_number": customer.phone_number,
                    "type": "online",
                    "created_at": customer.created_at.isoformat() if customer.created_at else None,
                    "created_at_raw": customer.created_at,  # For sorting
                    "image": customer.image
                })
            
            for customer in walkin_customers:
                all_customers.append({
                    "id": customer.walk_in_id,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "middle_initial": customer.middle_initial,
                    "phone_number": customer.phone_number,
                    "type": "walkin",
                    "created_at": customer.created_at.isoformat() if customer.created_at else None,
                    "created_at_raw": customer.created_at,  # For sorting
                    "image": None
                })
            
            # Sort the merged list based on sort_by
            def safe_sort_key(x):
                if sort_by == "name":
                    return (x['first_name'] or '').lower()
                elif sort_by == "phone":
                    return x['phone_number'] or ''
                else:  # created_at
                    created = x['created_at_raw']
                    if created is None:
                        return datetime(1900, 1, 1)
                    # Remove timezone info if present to avoid comparison issues
                    if hasattr(created, 'tzinfo') and created.tzinfo is not None:
                        return created.replace(tzinfo=None)
                    return created
            
            all_customers.sort(key=safe_sort_key, reverse=is_descending)
            
            # Apply pagination to the merged list
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            customers = all_customers[start_idx:end_idx]
            
            # Remove the raw created_at field used for sorting
            for customer in customers:
                customer.pop('created_at_raw', None)
            
            # Calculate pagination info
            total_pages = (total_count + limit - 1) // limit
            
            return jsonify({
                "status": True,
                "message": "Customers retrieved successfully",
                "customers": customers,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "total_pages": total_pages,
                    "online_count": online_count,
                    "walkin_count": walkin_count
                }
            }), 200
            
        except Exception as e:
            db.session.rollback()
            print(f"Error in get_all_customers: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": False,
                "message": "Internal error",
                "error": str(e)
            }), 500
    
    
