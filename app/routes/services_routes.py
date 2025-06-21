from flask import Blueprint, request, jsonify
from app.models.service_model import Service
from app import db


service_bp = Blueprint("service", __name__)

@service_bp.route(rule="/create-service", methods=["POST"])
def create_service():
    try:
        data = request.json  
        service = Service.query.filter_by(service_name = data["service_name"]).limit(12).first()
        if service:
            return jsonify({"status": False, "message": "Service already exist"}), 409
        
        new_service = Service(
            service_name = data["service_name"],
            branch_id = data["branch_id"],
            price = data["price"],
            category = data["category"],
            image = data["image"],
        )
        db.session.add(new_service)
        db.session.commit()
        
        return jsonify({"status":True, "message":"added successfully", "branch":new_service.to_dict()}), 201

        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    

@service_bp.route(rule="/get-services", methods=["GET"])
def get_services():
    try:
        services = Service.query.all()
        return jsonify({"status": True, "message": "get successfully", "services": [service.to_dict() for service in services]}), 200
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500


@service_bp.route(rule="/delete-service", methods=["DELETE"])
def delete_service():
    try:
        data = request.json
        service = Service.query.filter_by(service_id=data["service_id"]).first()
        
        if not service:
            return jsonify({"status": False, "message":"service not found"}), 404
        
        db.session.delete(service)
        db.session.commit()
        
        return jsonify({"status": True, "message":"service deleted"}), 201

    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    

@service_bp.route(rule="/update-service", methods=["PUT"])
def update_service():
    try:
        data = request.json
        service = Service.query.filter_by(service_id=data["service_id"]).first()
        
        if not service:
            return jsonify({"status": False, "message": "service not found"}), 404
        
        # Only update if the key exists in the incoming JSON
        service.service_name = data.get("service_name", service.service_name)
        service.branch_id = data.get("branch_id", service.branch_id)
        service.price = data.get("price", service.price)
        service.category = data.get("category", service.category)
        service.image = data.get("image", service.image)
        
        db.session.commit()
        
        return jsonify({
            "status": True,
            "message": "Service updated successfully",
            "service": service.to_dict()
        })
        
    except Exception as e:
        return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500
