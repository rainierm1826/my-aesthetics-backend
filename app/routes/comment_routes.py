from flask import Blueprint, jsonify, request
from ..models.comment_model import Comment
from ..models.user_model import User
from ..extension import db
from flask_jwt_extended import get_jwt_identity, jwt_required

comment_bp = Blueprint("comment", __name__)


@comment_bp.route(rule="/create-comment", methods=["POST"])
@jwt_required()
def create_comment():
    try:
        data = request.json
        identity = get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()
        new_comment = Comment(
            user_id=user.user_id,
            comment=data["comment"]
        )
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify({"status":True, "message":"commented successfully", "comment":new_comment.to_dict()}), 201
    
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@comment_bp.route(rule="/get-comments", methods=["GET"])
def get_comments():
    try:
        comments = Comment.query.all()
        return jsonify({"status": True, "comment":[comment.to_dict() for comment in comments]})
    
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@comment_bp.route(rule="/get-comment", methods=["GET"])
@jwt_required()
def get_comment():
    try:
        identity = get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()
        comments = Comment.query.filter_by(user_id=user.user_id).all()
        return jsonify({"status": True, "comment":[comment.to_dict() for comment in comments]}) 
    
    except Exception as e:
        return jsonify({"status": False, "message":"Internal Error", "error": str(e)}), 500

@comment_bp.route(rule="/update-comment", methods=["PATCH"])
@jwt_required()
def update_comment():
    try:
        data = request.json
        identity = get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()

        comment = Comment.query.filter_by(comment_id=data["comment_id"], user_id=user.user_id).first()
        if not comment:
            return jsonify({"status": False, "message": "Comment not found or unauthorized"}), 404

        updatable_fields = ["comment"]
        for field in updatable_fields:
            if field in data:
                setattr(comment, field, data[field])
        db.session.commit()

        return jsonify({
            "status": True,
            "message": "Comment updated successfully",
            "comment": comment.to_dict()
        })

    except Exception as e:
        return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500

@comment_bp.route(rule="/delete-comment", methods=["DELETE"])
@jwt_required()
def delete_comment():
    try:
        data = request.json
        identity = get_jwt_identity()
        user = User.query.filter_by(account_id=identity).first()
        comment = Comment.query.filter_by(comment_id=data["comment_id"], user_id=user.user_id).first()
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            "status": True,
            "message": "Comment deleted successfully",
        })
    
    except Exception as e:
        return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500