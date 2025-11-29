from ..models.auth_model import Auth
from ..models.admin_model import Admin
from ..models.user_model import User
from ..models.otp_model import OTP
from ..models.owner_model import Owner
from ..models.aesthetician_model import Aesthetician
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
                if auth.is_verified and auth.role_id == "1" and not auth.isDeleted:
                    return jsonify({"status": False, "message": "Email already exists"}), 409
                
                if auth.role_id in ["2", "3"] and not auth.isDeleted:
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
            print("error: ", str(e))
            db.session.rollback()
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500
    
    def admin_signup(self):
        try:
            data = request.json
        
            auth = Auth.query.filter_by(email=data["email"]).first()
            
            if not self._validate_credentials(crendetials=data):
                return jsonify({"status": False, "message": "Missing email or password"}), 404
            
            # Check if email exists and if both auth AND admin are not deleted
            if auth:
                admin = Admin.query.filter_by(account_id=auth.account_id).first()
                
                # Block signup only if auth is not deleted AND (no admin OR admin is not deleted)
                if not auth.isDeleted and (not admin or not admin.isDeleted):
                    return jsonify({"status": False, "message": "Email already exists"}), 409

            email = data.pop("email")
            password = data.pop("password")
            
            # If email was deleted (either auth.isDeleted or admin.isDeleted), reactivate the account
            if auth:
                # Reactivate the auth account
                auth.password = password
                auth.isDeleted = False
                auth.is_verified = True
                auth.role_id = "2"  # Ensure it's set to admin role
                
                # Find and reactivate or update the admin record
                admin = Admin.query.filter_by(account_id=auth.account_id).first()
                if admin:
                    # Update existing admin with new data
                    for key, value in data.items():
                        setattr(admin, key, value)
                    admin.isDeleted = False
                else:
                    # Create new admin record if it doesn't exist
                    admin = Admin(account_id=auth.account_id, **data)
                    db.session.add(admin)
                
                db.session.commit()
                return jsonify({"status": True, "message": "Admin account reactivated successfully", "auth": auth.to_dict()}), 201
            
            # Create new auth and admin records
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
            
            if auth and not auth.isDeleted:
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
            # Get the first NON-DELETED auth record with this email
            auth = Auth.query.filter_by(email=data["email"], isDeleted=False).first()
            if not auth:
                return jsonify({"status": False, "message": "Wrong email"}), 404
            
            if auth.role_id == "1" and not auth.is_verified:
                return jsonify({"status": False, "message": "Wrong email"}), 403
            
            if not auth.check_password(data["password"]):
                return jsonify({"status": False, "message": "Wrong password"}), 404
            
            # Check if the related user record is deleted (for admins/aestheticians)
            try:
                if auth.role_id == "2":  # Admin
                    admin = Admin.query.filter_by(account_id=auth.account_id).first()
                    if admin and admin.isDeleted:
                        return jsonify({"status": False, "message": "Account has been deleted"}), 403
                # Note: Aestheticians are not directly linked to Auth records via account_id
                # They are managed separately, so we skip that check here
            except Exception as check_error:
                # Log the error but don't fail the login
                print(f"Error checking deleted status: {str(check_error)}")
            
            # Get role name safely
            role_name = auth.role.role_name if auth.role else "unknown"
            
            access_token = create_access_token(identity=auth.account_id, additional_claims={"email": auth.email, "role": role_name, "is_verified":auth.is_verified})
            refresh_token = create_refresh_token(identity=auth.account_id)
            response = make_response(jsonify({
                "status": True,
                "message": "login successfully",
                "auth": auth.to_dict(),
                "access_token":access_token,
            }))
            
            # Get environment-specific cookie settings
            import os
            is_production = os.getenv("ENVIRONMENT", "development") == "production"
            cookie_secure = is_production
            # Use Lax instead of None to avoid third-party cookie blocking in browsers
            cookie_samesite = "None"
            
            # Set domain for cookie sharing across subdomains
            # In production: .myaestheticsbrowstudio.com allows cookies to work on both
            # api.myaestheticsbrowstudio.com and myaestheticsbrowstudio.com
            cookie_domain = ".myaestheticsbrowstudio.com" if is_production else None
            
            # First, clear any existing cookies (including old SameSite=None cookies)
            # This ensures clean state for users with old cookies
            response.delete_cookie("access_token", secure=cookie_secure, samesite=cookie_samesite, domain=cookie_domain)
            response.delete_cookie("refresh_token", secure=cookie_secure, samesite=cookie_samesite, domain=cookie_domain)
            
            # Also try to delete with old SameSite=None settings in case they exist
            if is_production:
                response.delete_cookie("access_token", secure=True, samesite="None", domain=cookie_domain)
                response.delete_cookie("refresh_token", secure=True, samesite="None", domain=cookie_domain)
            
            # Now set fresh cookies with appropriate security settings
            response.set_cookie(
                "access_token", 
                access_token, 
                max_age=60 * 60 * 24 * 7, 
                httponly=True, 
                secure=cookie_secure,
                samesite=cookie_samesite,
                domain=cookie_domain
            )
            response.set_cookie(
                "refresh_token", 
                refresh_token, 
                max_age=60 * 60 * 24 * 7, 
                httponly=True, 
                secure=cookie_secure,
                samesite=cookie_samesite,
                domain=cookie_domain
            )
            return response
        except Exception as e:
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500
        
    def sign_out(self):
        try:
            response = make_response(jsonify({
            "status": True,
            "message": "logout successfully"
        }))
            
            # Get environment-specific cookie settings
            import os
            is_production = os.getenv("ENVIRONMENT", "development") == "production"
            cookie_secure = is_production
            # Use Lax instead of None to avoid third-party cookie blocking in browsers
            cookie_samesite = "None"
            cookie_domain = ".myaestheticsbrowstudio.com" if is_production else None
            
            # Delete cookies with the same settings they were set with
            response.delete_cookie("access_token", secure=cookie_secure, samesite=cookie_samesite, domain=cookie_domain)
            response.delete_cookie("refresh_token", secure=cookie_secure, samesite=cookie_samesite, domain=cookie_domain)
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


    def send_email_verification_otp(self):
        """
        Sends OTP to admin/owner email for email verification.
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
            return jsonify({"status": False, "message": "Internal Error", "error": str(e)}), 500

    def verify_email_otp(self):
        """
        Verifies OTP for email verification.
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
            
            # Mark email as verified
            auth.is_verified = True
            
            db.session.commit()

            return jsonify({"status": True, "message": "Email Verified Successfully"}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "Internal Error",
                "error": str(e)
            }), 500
    
    def _validate_credentials(self, crendetials):
        required_fields = ["email", "password"]
        for field in required_fields:
            if field not in crendetials:
                return False
        return True

    def change_password(self):
        """
        Changes user's password with current password verification.
        Expects: {"current_password": "old_pass", "new_password": "new_pass"}
        Requires: JWT authentication
        """
        try:
            from flask_jwt_extended import get_jwt_identity
            identity = get_jwt_identity()
            
            data = request.json
            
            if not data.get("current_password") or not data.get("new_password"):
                return jsonify({"status": False, "message": "Missing current_password or new_password"}), 400
            
            auth = Auth.query.filter_by(account_id=identity).first()
            if not auth:
                return jsonify({"status": False, "message": "User not found"}), 404
            
            # Verify current password
            if not auth.check_password(data["current_password"]):
                return jsonify({"status": False, "message": "Current password is incorrect"}), 401
            
            # Update password
            auth.password = data["new_password"]
            db.session.commit()
            
            return jsonify({"status": True, "message": "Password changed successfully"}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": False,
                "message": "Internal Error",
                "error": str(e)
            }), 500
    
    def refresh(self):
        try:
            from flask_jwt_extended import get_jwt_identity
            
            account_id = get_jwt_identity()
            auth = Auth.query.get(account_id)
            
            if not auth:
                return jsonify({"status": False, "message": "Account not found"}), 404
            
            if auth.isDeleted:
                return jsonify({"status": False, "message": "Account has been deleted"}), 403
            
            # Get role name for the new token
            try:
                role_name = auth.role.role_name if auth.role else "unknown"
            except Exception as role_error:
                print(f"DEBUG REFRESH - Error getting role: {role_error}")
                role_name = "unknown"
            
            # Generate new access token with all claims
            new_access_token = create_access_token(
                identity=account_id,
                additional_claims={
                    "email": auth.email,
                    "role": role_name,
                    "is_verified": auth.is_verified
                }
            )
            
            # Create response with updated cookie
            response = make_response(jsonify({
                "status": True,
                "message": "Token refreshed successfully",
                "access_token": new_access_token,
                "auth": auth.to_dict()
            }))
            
            # Get environment-specific cookie settings
            import os
            is_production = os.getenv("ENVIRONMENT", "development") == "production"
            cookie_secure = is_production
            cookie_samesite = "None"
            cookie_domain = ".myaestheticsbrowstudio.com" if is_production else None
            
            # Update the access_token cookie
            response.set_cookie(
                "access_token", 
                new_access_token, 
                max_age=60 * 60 * 24 * 7, 
                httponly=True, 
                secure=cookie_secure,
                samesite=cookie_samesite,
                domain=cookie_domain
            )
            
            return response
        
        except Exception as e:
            return jsonify({
                "status": False,
                "message": "Internal Error",
                "error": str(e)
            }), 500
    
    def verify_session(self):
        """Verify the current session and return user information"""
        try:
            from flask_jwt_extended import get_jwt_identity, get_jwt
            
            account_id = get_jwt_identity()
            claims = get_jwt()
            
            if not account_id:
                return jsonify({"status": False, "message": "Not authenticated"}), 401
            
            # Get the auth record to verify it still exists and is not deleted
            auth = Auth.query.get(account_id)
            
            if not auth or auth.isDeleted:
                return jsonify({"status": False, "message": "Account not found or deleted"}), 401
            
            # Check if related user record is deleted (for admins)
            if auth.role_id == "2":  # Admin
                admin = Admin.query.filter_by(account_id=auth.account_id).first()
                if admin and admin.isDeleted:
                    return jsonify({"status": False, "message": "Account has been deleted"}), 401
            
            # Return user information
            role_name = auth.role.role_name if auth.role else "unknown"
            
            return jsonify({
                "account_id": account_id,
                "email": claims.get("email", auth.email),
                "role": role_name,
                "is_verified": auth.is_verified
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": False,
                "message": "Invalid or expired token",
                "error": str(e)
            }), 401
    
    def check_cookies(self):
        """Debug endpoint to check cookie configuration"""
        import os
        from flask import request as flask_request
        
        cookies = flask_request.cookies
        is_production = os.getenv("ENVIRONMENT", "development") == "production"
        
        return jsonify({
            "environment": "production" if is_production else "development",
            "has_access_token": "access_token" in cookies,
            "has_refresh_token": "refresh_token" in cookies,
            "cookies_found": list(cookies.keys()),
            "cors_origins": ["http://localhost:3000", "https://my-aesthetics-three.vercel.app", "https://myaestheticsbrowstudio.com", "https://my-aesthetics-frontend.onrender.com"],
            "cookie_settings": {
                "secure": is_production,
                "samesite": "None",  
                "httponly": True
            }
        }), 200
    
    def clear_cookies(self):
        """Endpoint to forcefully clear all auth cookies - useful for migration"""
        import os
        
        is_production = os.getenv("ENVIRONMENT", "development") == "production"
        cookie_secure = is_production
        cookie_domain = ".myaestheticsbrowstudio.com" if is_production else None
        
        response = make_response(jsonify({
            "status": True,
            "message": "All auth cookies cleared successfully"
        }))
        
        # Clear with Lax settings (current)
        response.delete_cookie("access_token", secure=cookie_secure, samesite="Lax", domain=cookie_domain)
        response.delete_cookie("refresh_token", secure=cookie_secure, samesite="Lax", domain=cookie_domain)
        
        # Also clear with None settings (old cookies that might still exist)
        if is_production:
            response.delete_cookie("access_token", secure=True, samesite="None", domain=cookie_domain)
            response.delete_cookie("refresh_token", secure=True, samesite="None", domain=cookie_domain)
        
        # Also try without domain (edge case)
        response.delete_cookie("access_token", secure=cookie_secure, samesite="Lax")
        response.delete_cookie("refresh_token", secure=cookie_secure, samesite="Lax")
        
        if is_production:
            response.delete_cookie("access_token", secure=True, samesite="None")
            response.delete_cookie("refresh_token", secure=True, samesite="None")
        
        return response