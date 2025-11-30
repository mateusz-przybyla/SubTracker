from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from typing import Any

from api.schemas import ReminderSendTestSchema
from workers import mail_worker

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
    
@blp.route("/reminders/send-test")
class ReminderSendTest(MethodView):
    @blp.arguments(ReminderSendTestSchema)
    @blp.response(200, description="Test email sent successfully")
    def post(self, args: dict[str, Any]) -> dict[str, Any]:
        """
        Developer-only endpoint to send a test reminder email.
        Useful for verifying email templates and Mailgun integration.
        """
        response = mail_worker.send_email_reminder(
            user_email=args['email'],
            subscription_name=args['subscription_name'],
            next_payment_date=args['next_payment_date'],
        )

        return {"status": "ok", "mailgun_status": response.status_code}