from flask import Blueprint, request, jsonify
from ..models.aesthetician_model import Aesthetician
from ..extension import db
from sqlalchemy.sql import func

aesthetician_bp = Blueprint("aesthetician", __name__)

@aesthetician_bp.route(rule="/create-aesthetician", methods=["POST"])
def create_aesthetician():
    try:
        data = request.json
        
        new_aesthetician = Aesthetician(
            branch_id=data["branch_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            middle_initial=data["middle_initial"],
            phone_number=data["phone_number"],
            image=data["image"],
            sex=data["sex"],
            experience=data["experience"]
        )
        
        db.session.add(new_aesthetician)
        db.session.commit()
        
        
        return jsonify({"status":True, "message":"created successfully", "branch":new_aesthetician.to_dict()}), 201
        
        
    except Exception as e:       
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@aesthetician_bp.route(rule="/get-aestheticians", methods=["GET"])
def get_aestheticians():
    try:
        aestheticians = Aesthetician.query.all()
        
        return jsonify({"status":True, "message":"get successfully", "aesthetician": [aesthetician.to_dict() for aesthetician in aestheticians]})

    except Exception as e:       
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    
@aesthetician_bp.route(rule="/update-aesthetician", methods=["PATCH"])
def update_aesthetician():
    try:
        data = request.json
        aesthetician = Aesthetician.query.filter_by(aesthetician_id=data["aesthetician_id"]).first()
        if not aesthetician:
            return jsonify({"status": False, "message":"aesthetician not found"}), 404
        
        updateble_fields = ["first_name", "last_name", "middle_initial", "sex",  "experience", "image"]
        
        for field in updateble_fields:
            if field in data:
                setattr(aesthetician, field, data[field])
        db.session.commit()
        return jsonify({"status":True, "message":"updated successfully", "aesthetician": aesthetician.to_dict()})
    except Exception as e:       
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@aesthetician_bp.route(rule="/delete-aesthetician", methods=["DELETE"])
def delete_aesthetician():
    try:
        data = request.json
        aesthetician = Aesthetician.query.filter_by(aesthetician_id=data["aesthetician_id"]).first()
        if not aesthetician:
            return jsonify({"status": False, "message":"aesthetician not found"}), 404
        
        db.session.delete(aesthetician)
        db.session.commit()
        return jsonify({"status": True, "message":"deleted successfully"})
    except Exception as e:       
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

    