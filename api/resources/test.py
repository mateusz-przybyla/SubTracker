from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from api.extensions import db
from api.models import UserModel, SubscriptionModel, ReminderLogModel
from datetime import date

blp = Blueprint("test", __name__, description="Test endpoints")

@blp.route("/guest")
class TestGuestEndpoint(MethodView):
    def get(self):
        return {"message": "This endpoint is open to everyone."}

@blp.route("/protected")
class TestAuthEndpoint(MethodView):
    @jwt_required()
    def get(self):
        return {"message": "This is a protected endpoint."}
    
@blp.route("/fresh-protected")
class TestFreshAuthEndpoint(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        return {"message": "This is a protected endpoint. You used a fresh token to access it."}
    
@blp.route("/add-subscription")
class SubscriptionEndpoint(MethodView):
    def get(self):
        user = UserModel.query.first()
        if not user:
            abort(404, message="No user found to add subscription.")

        subscription = SubscriptionModel(
            user_id=user.id,
            name="Test Subscription",
            price=9.99,
            billing_cycle="monthly",
            next_payment_date=date.today()
        )
        db.session.add(subscription)
        db.session.commit()

        return {"message": "Subscription created", "subscription": {
            "id": subscription.id,
            "name": subscription.name,
            "price": str(subscription.price),
            "billing_cycle": subscription.billing_cycle,
            "next_payment_date": subscription.next_payment_date.isoformat()
        }}
    
@blp.route("/add-reminder-log") 
class ReminderLogEndpoint(MethodView):
    def get(self):
        sub = SubscriptionModel.query.first()
        if not sub:
            abort(404, message="No subscription found to add reminder log.")

        reminder_log = ReminderLogModel(
            subscription_id=sub.id,
            message="Reminder sent successfully.",
            success=True
        )
        db.session.add(reminder_log)
        db.session.commit()

        return {"message": "Reminder log created", "reminder_log": {
            "subscription_id": reminder_log.subscription_id,
            "message": reminder_log.message,
            "success": reminder_log.success,
            "sent_at": reminder_log.sent_at.isoformat()
        }}

@blp.route("/get-subscriptions")    
class GetSubscriptionsEndpoint(MethodView):
    def get(self):
        user = UserModel.query.first()
        if not user:
            abort(404, message="No user found.")

        subscriptions = SubscriptionModel.query.filter_by(user_id=user.id).all()
        return {"subscriptions": [
            {
                "id": sub.id,
                "name": sub.name,
                "price": str(sub.price),
                "billing_cycle": sub.billing_cycle,
                "next_payment_date": sub.next_payment_date.isoformat()
            } for sub in subscriptions
        ]}