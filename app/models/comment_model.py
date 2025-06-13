from app import db
from uuid import uuid4
from datetime import datetime, timezone

class Comment(db.Model):
    comment_id = db.Column(db.String(255), primary_key=True, default=lambda:str(uuid4()))
    user_id = db.Column(db.String(255), db.ForeignKey("user.user_id"))
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    user = db.relationship("User", backref="comments")
    