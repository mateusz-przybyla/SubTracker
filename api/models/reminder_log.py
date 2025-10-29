from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from api.extensions import db

class ReminderLogModel(db.Model):
    __tablename__ = "reminder_logs"

    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey("subscriptions.id"), nullable=False)
    message = db.Column(db.Text, nullable=True)
    success = db.Column(db.Boolean, default=True)

    sent_at = db.Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    subscription = db.relationship("SubscriptionModel", back_populates="reminders")

    def __repr__(self):
        return f"<ReminderLog sub_id={self.subscription_id} sent_at={self.sent_at}>"
