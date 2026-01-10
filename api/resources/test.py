from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from typing import Any
from sqlalchemy.exc import SQLAlchemyError

from api.extensions import db
from api.models import UserModel
from api.schemas import (
    ReminderSendTestSchema, 
    StatsSendTestSchema, 
    UserResponseSchema
)
from api.tasks import email_tasks

blp = Blueprint("test", __name__, description="Developer endpoints (authentication tests, email tests, etc.)")

@blp.route("/guest")
class TestGuestEndpoint(MethodView):
    @blp.response(200, description="Guest endpoint accessed successfully.")
    def get(self) -> dict[str, str]:
        """
        Developer test endpoint that demonstrates an open route.
        Accessible without authentication or JWT token.
        Useful for verifying that the API is reachable without protection.
        """
        return {"message": "This endpoint is open to everyone."}

@blp.route("/protected")
class TestAuthEndpoint(MethodView):
    @jwt_required()
    @blp.response(200, description="Protected endpoint accessed successfully.")
    @blp.alt_response(401, description="Missing or invalid token.")
    def get(self) -> dict[str, str]:
        """
        Developer test endpoint that requires a valid JWT token.
        Demonstrates how protected routes behave when accessed with or without authentication.
        """
        return {"message": "This is a protected endpoint."}
    
@blp.route("/fresh-protected")
class TestFreshAuthEndpoint(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, description="Fresh protected endpoint accessed successfully.")
    @blp.alt_response(401, description="Missing or invalid fresh token.")
    def get(self) -> dict[str, str]:
        """
        Developer test endpoint that requires a fresh JWT token.
        Demonstrates stricter authentication after login.
        """
        return {"message": "This is a protected endpoint. You used a fresh token to access it."}
       
@blp.route("/users/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserResponseSchema, description="User details retrieved successfully.")
    @blp.alt_response(404, description="User not found.")
    def get(self, user_id: int) -> UserModel:
        """Developer endpoint to retrieve user details by user ID."""
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found.")
        return user
    
    @blp.response(200, description="User deleted successfully.")
    @blp.alt_response(404, description="User not found.")
    def delete(self, user_id: int) -> dict[str, str]:
        """Developer endpoint to delete a user by user ID."""
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found.")

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the user.")

        return {"message": "User deleted."}
    
@blp.route("/reminders/send-test")
class ReminderSendTest(MethodView):
    @blp.arguments(ReminderSendTestSchema)
    @blp.response(200, description="Test reminder email sent successfully.")
    def post(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        Developer-only endpoint to send a test reminder email.
        Useful for verifying email templates and Mailgun integration.
        """
        response = email_tasks.send_email_reminder(
            user_email=args['email'],
            subscription_name=args['subscription_name'],
            next_payment_date=args['next_payment_date'],
        )
        return {"status": "ok", "mailgun_status": response.status_code}
    
@blp.route("/stats/send-test")
class StatsSendTest(MethodView):
    @blp.arguments(StatsSendTestSchema)
    @blp.response(200, description="Test stats summary email sent successfully.")
    def post(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        Developer-only endpoint to send a test stats summary email.
        Useful for verifying monthly summary email templates and Mailgun integration.
        """
        summary = {
            "month": args['month'],
            "total_spent": args['total_spent'],
            "by_category": args['by_category'],
        }
        response = email_tasks.send_monthly_summary_email(
            user_email=args['email'], 
            summary=summary
        )
        return {"status": "ok", "mailgun_status": response.status_code}