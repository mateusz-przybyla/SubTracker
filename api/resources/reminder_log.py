from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import List

from api.schemas import ReminderLogSchema
from api.models import ReminderLogModel
from api.services import reminder_log as reminder_log_service

blp = Blueprint("reminder_log", __name__, description="Endpoints for tracking and retrieving reminder delivery logs")

@blp.route("/subscriptions/<int:sub_id>/reminder_logs")
class ReminderLogList(MethodView):
    @jwt_required()
    @blp.response(200, ReminderLogSchema(many=True), description="List of reminder logs for a subscription.")
    @blp.alt_response(404, description="Subscription not found.")
    def get(self, sub_id: int) -> List[ReminderLogModel]:
        user_id = get_jwt_identity()
        return reminder_log_service.get_reminder_logs_by_subscription(sub_id, user_id)

@blp.route("/reminder_logs/<int:log_id>")
class ReminderLog(MethodView):
    @jwt_required()
    @blp.response(200, ReminderLogSchema)
    @blp.alt_response(404, description="Reminder log not found.")
    def get(self, log_id: int) -> ReminderLogModel:
        return reminder_log_service.get_reminder_log_by_id(log_id)

    @jwt_required()
    @blp.response(200, description="Reminder log deleted successfully.")
    @blp.alt_response(404, description="Reminder log not found.")
    def delete(self, log_id: int) -> dict[str, str]:
        reminder_log_service.delete_reminder_log(log_id)
        return {"message": "Reminder log deleted."} 