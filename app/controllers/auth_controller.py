from ..models.auth_model import Auth
from ..models.admin_model import Admin
from ..models.user_model import User
from ..models.otp_model import OTP
from ..models.owner_model import Owner
from flask import jsonify, request, make_response
from ..extension import db
from datetime import datetime, timedelta, timezone
from ..helper.functions import generate_otp, send_email_otp
from flask_jwt_extended import create_access_token, create_refresh_token
from ..controllers.base_crud_controller import BaseCRUDController



class AuthController(BaseCRUDController):
    def __init__(self):
        super().__init__(
            model=Auth,
            id_field="account_id",
            
        )
    
    def customer_signup(self):
        try:
            data = request.json
            data["role_id"] = "1"
            
            auth = Auth.query.filter_by(email=data["email"]).first()
            
            if not self._validate_credentials(data):
                return jsonify({"status": False, "message": "Missing email or password"}), 404
        
            if auth:
                if auth.is_verified and auth.role_id == "1":
                    return jsonify({"status": False, "message": "Email already exists"}), 409
                
                if auth.role_id in ["2", "3"]:
                    return jsonify({"status": False, "message": "Email already exists"}), 409
                
                else:
                    OTP.query.filter_by(email=data["email"]).delete()                    
                    
                    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=5)
                    otp = generate_otp()
                    new_otp = OTP(otp_code=otp, expires_at=expiration_time, email=data["email"])
                    db.session.add(new_otp)
                    db.session.commit() 
                    send_email_otp(to_email=data["email"], otp=otp)
                    return jsonify({"status": True, "message": "New OTP sent to email"}), 200
            
            new_auth = Auth(**data)
            db.session.add(new_auth)
            db.session.flush()
            
            new_user = User(account_id=new_auth.account_id)
            db.session.add(new_user)
            db.session.flush()
            
            
            expiration_time = datetime.now(timezone.utc) + timedelta(minutes=5)
            otp = generate_otp()
            new_otp = OTP(otp_code=otp, expires_at=expiration_time, email=data["email"])
            db.session.add(new_otp)
            db.session.commit()
            
            send_email_otp(to_email=data["email"],otp=otp)
            
            return jsonify({"status": True, "message": "OTP sent to email successfully", "auth":new_auth.to_dict()})
                
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500
    
    def admin_signup(self):
        try:
            data = request.json
        
            auth = Auth.query.filter_by(email=data["email"]).first()
            
            if auth:
                return jsonify({"status": False, "message": "Email already exists"}), 409

            if not self._validate_credentials(crendetials=data):
                return jsonify({"status": False, "message": "Missing email or password"}), 404

            email = data.pop("email")
            password = data.pop("password")
            new_auth = Auth(email=email, password=password, role_id="2")
            db.session.add(new_auth)
            db.session.flush()

            new_user = Admin(account_id=new_auth.account_id, **data)
            db.session.add(new_user)
            db.session.flush()

            db.session.commit()

            return jsonify({"status": True, "message": "Admin created successfully", "auth":new_auth.to_dict()}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500

    def owner_signup(self):
        try:
            data = request.json
        
            auth = Auth.query.filter_by(email=data["email"]).first()
            
            if auth:
                return jsonify({"status": False, "message": "Email already exists"}), 409

            if not self._validate_credentials(crendetials=data):
                return jsonify({"status": False, "message": "Missing email or password"}), 404

            new_auth = Auth(email=data["email"], password=data["password"], role_id="3")
            db.session.add(new_auth)
            db.session.flush()

            new_user = Owner(account_id=new_auth.account_id)
            db.session.add(new_user)
            db.session.flush()
            db.session.commit()

            return jsonify({"status": True, "message": "Owner created successfully", "auth":new_auth.to_dict()}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500
    
    def request_otp(self):
        try:
            data = request.json
            
            if not data["email"]:
                return jsonify({"status": False, "message": "Missing email"}), 400

            auth = Auth.query.filter_by(email=data["email"]).first()

            if auth and auth.is_verified:
                return jsonify({"status": False, "message": "Email already exists"}), 409

            if auth and not auth.is_verified:
                OTP.query.filter_by(email=data["email"]).delete()
                db.session.commit()

            # Generate a new OTP
            expiration_time = datetime.now(timezone.utc) + timedelta(minutes=5)
            otp = generate_otp()

            new_otp = OTP(otp_code=otp, expires_at=expiration_time, email=data["email"])
            db.session.add(new_otp)
            db.session.commit()

            send_email_otp(to_email=data["email"], otp=otp)

            return jsonify({"status": True, "message": "OTP sent to email successfully"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "Internal Error",
                "error": str(e)
            }), 500

    def verify_otp(self):
        try:
            data = request.json

            auth = Auth.query.filter_by(email=data["email"]).first()
            if not auth:
                return jsonify({"status": False, "message": "User not found"}), 404

            otp = OTP.query.filter_by(email=data["email"], otp_code=data["otp_code"], is_used=False).first()
            if not otp:
                return jsonify({"status": False, "message": "Invalid OTP"}), 400

            # Check expiry
            if datetime.now(timezone.utc) > otp.expires_at:
                return jsonify({"status": False, "message": "OTP Expired"}), 400

            # Success
            auth.is_verified = True
            otp.is_used = True
            db.session.commit()

            return jsonify({"status": True, "message": "OTP Verified Successfully"}), 200

        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500


    def signin(self):
        try:
            data = request.json
            auth = Auth.query.filter_by(email=data["email"]).first()
            if not auth:
                return jsonify({"status": False, "message": "Wrong email"}), 404
            
            if auth.role_id == "1" and not auth.is_verified:
                return jsonify({"status": False, "message": "Wrong email"}), 403
            
            if not auth.check_password(data["password"]):
                return jsonify({"status": False, "message": "Wrong password"}), 404
            access_token = create_access_token(identity=auth.account_id, additional_claims={"email": auth.email, "role":auth.role.role_name, "is_verified":auth.is_verified})
            refresh_token = create_refresh_token(identity=auth.account_id)
            response = make_response(jsonify({
                "status": True,
                "message": "login successfully",
                "auth": auth.to_dict(),
                "access_token":access_token,
            }))
            response.set_cookie("access_token", access_token, max_age=60 * 60 * 24 * 7, httponly=True, secure=False)
            response.set_cookie("refresh_token", refresh_token, max_age=60 * 60 * 24 * 7, httponly=True, secure=False)
            return response
        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500
        
    def sign_out(self):
        try:
            response = make_response(jsonify({
            "status": True,
            "message": "logout successfully"
        }))
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        except Exception as e:
            return jsonify({"status": False, "message":"Internal Error"}), 500
    
    def forgot_password(self):
        """
        Initiates forgot password flow by sending OTP to user's email.
        Expects: {"email": "user@example.com"}
        """
        try:
            data = request.json
            
            if not data.get("email"):
                return jsonify({"status": False, "message": "Missing email"}), 400

            auth = Auth.query.filter_by(email=data["email"]).first()

            if not auth:
                # For security, don't reveal if email exists
                return jsonify({"status": True, "message": "If email exists, OTP will be sent"}), 200

            # Delete any existing OTP for this email
            OTP.query.filter_by(email=data["email"]).delete()
            db.session.commit()

            # Generate new OTP
            expiration_time = datetime.now(timezone.utc) + timedelta(minutes=5)
            otp = generate_otp()

            new_otp = OTP(otp_code=otp, expires_at=expiration_time, email=data["email"])
            db.session.add(new_otp)
            db.session.commit()

            send_email_otp(to_email=data["email"], otp=otp)

            return jsonify({"status": True, "message": "OTP sent to email successfully"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "Internal Error",
                "error": str(e)
            }), 500

    def verify_otp_forgot_password(self):
        """
        Verifies OTP for password reset.
        Expects: {"email": "user@example.com", "otp_code": "123456"}
        """
        try:
            data = request.json

            if not data.get("email") or not data.get("otp_code"):
                return jsonify({"status": False, "message": "Missing email or OTP"}), 400

            auth = Auth.query.filter_by(email=data["email"]).first()
            if not auth:
                return jsonify({"status": False, "message": "User not found"}), 404

            otp = OTP.query.filter_by(
                email=data["email"], 
                otp_code=data["otp_code"], 
                is_used=False
            ).first()
            
            if not otp:
                return jsonify({"status": False, "message": "Invalid OTP"}), 400

            # Check expiry
            if datetime.now(timezone.utc) > otp.expires_at:
                return jsonify({"status": False, "message": "OTP Expired"}), 400

            # Mark OTP as used
            otp.is_used = True
            db.session.commit()

            return jsonify({"status": True, "message": "OTP Verified Successfully"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500

    def reset_password(self):
        """
        Resets user password after OTP verification.
        Expects: {"email": "user@example.com", "new_password": "newpass123"}
        """
        try:
            data = request.json

            if not data.get("email") or not data.get("new_password"):
                return jsonify({"status": False, "message": "Missing email or new password"}), 400

            auth = Auth.query.filter_by(email=data["email"]).first()
            if not auth:
                return jsonify({"status": False, "message": "User not found"}), 404

            # Check if there's a recently verified OTP
            recent_otp = OTP.query.filter_by(
                email=data["email"],
                is_used=True
            ).order_by(OTP.created_at.desc()).first()

            if not recent_otp:
                return jsonify({"status": False, "message": "Please verify OTP first"}), 400

            # Double-check OTP hasn't expired (extra security)
            now = datetime.now(timezone.utc)
            if now > recent_otp.expires_at:
                return jsonify({"status": False, "message": "OTP verification expired, please request new OTP"}), 400

            # Update password (Auth model automatically hashes it via property setter)
            auth.password = data["new_password"]
            db.session.commit()

            return jsonify({"status": True, "message": "Password reset successfully"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500

    
    def _validate_credentials(self, crendetials):
        required_fields = ["email", "password"]
        for field in required_fields:
            if field not in crendetials:
                return False
        return True