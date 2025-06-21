from flask import Blueprint, request, jsonify
from app import db
from app.models.branch_model import Branch
from app.models.address_model import Address

branch_bp = Blueprint("branch", __name__)


@branch_bp.route(rule="/create-branch", methods=["POST"])
def create_branch():
    try:
        data = request.json
        branch = Branch.query.filter_by(branch_name=data["branch_name"]).first()
        
        if branch:
            return jsonify({"status":False, "message":"branch already exist"}), 409
        
        new_address = Address(
            region=data["region"],
            province=data["province"],
            city=data["city"],
            barangay=data["barangay"],
            lot=data["lot"],
        )
        
        db.session.add(new_address)
        db.session.flush()
            
        new_branch = Branch(
            branch_name = data["branch_name"],
            image = data["image"],
            address_id = new_address.address_id
            )
        db.session.add(new_branch)
        db.session.commit()
            
        return jsonify({"status":True, "message":"created successfully", "branch":new_branch.to_dict()}), 201
    
    except Exception as e:       
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500
    

@branch_bp.route(rule="/get-branches", methods=["GET"])
def get_branches():
    try:
        branches = Branch.query.all()
        return jsonify({"status":True, "message":"get successfully", "branches": [branch.to_dict() for branch in branches]})
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500


@branch_bp.route(rule="/get-branch/<string:branch_id>", methods=["GET"])
def get_branch(branch_id):
    try:
        branch = Branch.query.filter_by(branch_id=branch_id).first()
        
        print(branch_id)
        
        if not branch:
            return jsonify({"status": False, "message":"branch not found"}), 404
        
        return jsonify({"status":True, "message":"get successfully", "branch": branch.to_dict()})
        
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500


@branch_bp.route(rule="/delete-branch", methods=["DELETE"])
def delete_branch():
    try:
        data = request.json
        branch = Branch.query.filter_by(branch_id=data["branch_id"]).first()
        
        if not branch:
            return jsonify({"status": False, "message":"branch not found"}), 404
        
        db.session.delete(branch)
        db.session.commit()
        
        return jsonify({"status": True, "message":"deleted successfully"})
    
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500


@branch_bp.route("/update-branch/<string:branch_id>", methods=["PUT"])
def update_branch(branch_id):
    try:
        data = request.json
        branch = Branch.query.filter_by(branch_id=branch_id).first()

        if not branch:
            return jsonify({"status": False, "message": "Branch not found"}), 404

        branch.branch_name = data.get("branch_name", branch.branch_name)
        branch.image = data.get("image", branch.image)

        if branch.address:
            branch.address.region = data.get("region", branch.address.region)
            branch.address.province = data.get("province", branch.address.province)
            branch.address.city = data.get("city", branch.address.city)
            branch.address.barangay = data.get("barangay", branch.address.barangay)
            branch.address.lot = data.get("lot", branch.address.lot)

        db.session.commit()

        return jsonify({
            "status": True,
            "message": "Branch updated successfully",
            "branch": branch.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": False,
            "message": "Internal Error",
            "error": str(e)
        }), 500
