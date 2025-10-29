from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from api.extensions import db

class UserModel(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    created_at = db.Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(TIMESTAMP(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)

    # Relationships
    subscriptions = db.relationship("SubscriptionModel", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} username={self.username} email={self.email}>"