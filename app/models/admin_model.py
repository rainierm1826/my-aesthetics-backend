from ..extension import db
from datetime import datetime, timezone
from ..helper.functions import generate_id


class Admin(db.Model):
    admin_id = db.Column(db.String(255), primary_key=True, default=generate_id("ADMIN"))
    account_id = db.Column(db.String(255), db.ForeignKey("auth.account_id"), nullable=False)
    branch_id = db.Column(db.String(255), db.ForeignKey("branch.branch_id"), nullable=False)
    admin_name = db.Column(db.String(255))
    image = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    auth = db.relationship("Auth", backref="auths")
    branch = db.relationship("Branch", backref="branches")
    
    
    def to_dict(self):
        return {
            "admin_id": self.admin_id,
            "account_id": self.account_id,
            "branch": {
                "branch_id": self.branch.branch_id,
                "branch_name": self.branch.branch_name
            },
            "admin_name": self.admin_name,
            "image": self.image,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    