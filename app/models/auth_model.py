from app import db
from uuid import uuid4
from datetime import datetime, timezone
from bcrypt import hashpw, checkpw, gensalt

class Auth(db.Model):
    account_id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid4()))
    provider = db.Column(db.String(255))
    provider_id = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    role_id = db.Column(db.String(255), db.ForeignKey("role.role_id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    role = db.relationship("Role", backref="auths")

    @staticmethod
    def hash_password(password):
        return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

    def check_password(self, password):
        return checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "provider": self.provider,
            "provider_id": self.provider_id,
            "email": self.email,
            "role": self.role.role_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
