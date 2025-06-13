from app import db

class UserRole(db.Model):
    __tablename__ = "user_role"

    account_id = db.Column(db.String(255), db.ForeignKey("auth.account_id"), primary_key=True)
    role_id = db.Column(db.String(255), db.ForeignKey("role.role_id"), primary_key=True)

    auth = db.relationship("Auth", backref="user_roles")
    role = db.relationship("Role", backref="user_roles")

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "role_id": self.role_id,
            "role": self.role.role,  
        }
