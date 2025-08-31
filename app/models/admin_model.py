from ..extension import db
from datetime import datetime, timezone
from ..helper.functions import generate_id


class Admin(db.Model):
    admin_id = db.Column(db.String(255), primary_key=True, default=lambda:generate_id("ADMIN"))
    account_id = db.Column(db.String(255), db.ForeignKey("auth.account_id"), nullable=False)
    branch_id = db.Column(db.String(255), db.ForeignKey("branch.branch_id"), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    middle_initial = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(255))
    birthday = db.Column("birthday", db.DateTime)
    image = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    auth = db.relationship("Auth", backref="admins")
    branch = db.relationship("Branch", backref="branches")
    
    @property
    def age(self):
        if not self.birthday:
            return None
    
    
    def to_dict(self):
        return {
            "user_id": self.admin_id,
            "account_id": self.account_id,
            "branch": {
                "branch_id": self.branch.branch_id,
                "branch_name": self.branch.branch_name
            },
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_initial": self.middle_initial,
            "image": self.image,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "age": self.age,
            "phone_number":self.phone_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    