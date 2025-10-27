from flask import request, jsonify
from ..extension import db
from ..models.walk_in_model import WalkIn
from datetime import datetime, timezone

def create_walk_in_customer():
    """Create a new walk-in customer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get("first_name") or not data.get("last_name"):
            return jsonify({"error": "First name and last name are required"}), 400
        
        # Create new walk-in customer
        new_walk_in = WalkIn(
            first_name=data.get("first_name", "").strip(),
            last_name=data.get("last_name", "").strip(),
            middle_initial=data.get("middle_initial", "").strip() or None,
            phone_number=data.get("phone_number", "").strip() or None,
        )
        
        db.session.add(new_walk_in)
        db.session.commit()
        
        return jsonify({
            "message": "Walk-in customer created successfully",
            "status": True,
            "walk_in": new_walk_in.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



def update_walk_in_customer():
    """Update a walk-in customer"""
    try:
        data = request.get_json()
        walk_in_id = data.get("walk_in_id")
        
        if not walk_in_id:
            return jsonify({"error": "walk_in_id is required"}), 400
        
        walk_in = WalkIn.query.filter_by(walk_in_id=walk_in_id).first()
        if not walk_in:
            return jsonify({"error": "Walk-in customer not found"}), 404
        
        # Update fields
        if "first_name" in data:
            walk_in.first_name = data.get("first_name", "").strip()
        if "last_name" in data:
            walk_in.last_name = data.get("last_name", "").strip()
        if "middle_initial" in data:
            walk_in.middle_initial = data.get("middle_initial", "").strip() or None
        if "phone_number" in data:
            walk_in.phone_number = data.get("phone_number", "").strip() or None
        
        walk_in.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            "message": "Walk-in customer updated successfully",
            "status": True,
            "walk_in": walk_in.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def delete_walk_in_customer():
    """Soft delete a walk-in customer"""
    try:
        data = request.get_json()
        walk_in_id = data
        
        if not walk_in_id:
            return jsonify({"error": "walk_in_id is required"}), 400
        
        walk_in = WalkIn.query.filter_by(walk_in_id=walk_in_id).first()
        if not walk_in:
            return jsonify({"error": "Walk-in customer not found"}), 404
        
        # Soft delete by setting isDeleted to True
        walk_in.isDeleted = True
        walk_in.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            "message": "Walk-in customer deleted successfully",
            "status": True
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
