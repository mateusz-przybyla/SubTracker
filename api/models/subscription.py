from sqlalchemy import DateTime
from sqlalchemy.sql import func
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

    created_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = db.relationship("UserModel", back_populates="subscriptions")
    reminders = db.relationship("ReminderLogModel", back_populates="subscription", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='unique_user_subscription_name'),
    )

    def __repr__(self):
        return f"<Subscription id={self.id} name={self.name} user_id={self.user_id}>"