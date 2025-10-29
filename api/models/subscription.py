from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from api.extensions import db

class SubscriptionModel(db.Model):
    __tablename__ = "subscriptions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    billing_cycle = db.Column(db.String(20), nullable=False)
    next_payment_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(80), nullable=True)

    created_at = db.Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(TIMESTAMP(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False)

    # Relationships
    user = db.relationship("UserModel", back_populates="subscriptions")
    reminders = db.relationship("ReminderLogModel", back_populates="subscription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subscription id={self.id} name={self.name} user_id={self.user_id}>"