from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.schemas import ReminderLogSchema
from api.services.reminder_log import get_reminder_log_by_id, create_reminder_log, delete_reminder_log, get_reminder_logs_by_subscription, check_if_subscription_exists

blp = Blueprint("reminder_log", __name__, description="Operations on reminder logs")

@blp.route("/subscriptions/<int:sub_id>/reminder_logs")
class ReminderLogList(MethodView):
    @jwt_required()
    @blp.response(200, ReminderLogSchema(many=True), description="List of reminder logs for a subscription.")
    @blp.alt_response(404, description="Subscription not found.")
    def get(self, sub_id):
        user_id = get_jwt_identity()
        return get_reminder_logs_by_subscription(sub_id, user_id)

    # post endpoint for debugging purposes only
    @jwt_required()
    @blp.arguments(ReminderLogSchema)
    @blp.response(201, ReminderLogSchema, description="Reminder log created successfully.")
    @blp.alt_response(404, description="Subscription not found.")
    def post(self, data, sub_id):
        user_id = get_jwt_identity()
        check_if_subscription_exists(sub_id, user_id)
        return create_reminder_log(data, sub_id)

@blp.route("/reminder_logs/<int:log_id>")
class ReminderLog(MethodView):
    @jwt_required()
    @blp.response(200, ReminderLogSchema)
    @blp.alt_response(404, description="Reminder log not found.")
    def get(self, log_id):
        return get_reminder_log_by_id(log_id)

    @jwt_required()
    @blp.response(200, description="Reminder log deleted successfully.")
    @blp.alt_response(404, description="Reminder log not found.")
    def delete(self, log_id):
        delete_reminder_log(log_id)
        return {"message": "Reminder log deleted."}