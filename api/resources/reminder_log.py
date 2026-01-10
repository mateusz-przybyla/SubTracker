from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import List

from api.schemas import ReminderLogResponseSchema
from api.models import ReminderLogModel
from api.services import reminder_log as reminder_log_service
from api.docs.common_responses import apply_common_responses, RESOURCE_ERRORS

blp = Blueprint("reminder_log", __name__, description="Endpoints for tracking and retrieving reminder delivery logs")

@blp.route("/subscriptions/<int:sub_id>/reminder_logs")
class ReminderLogList(MethodView):
    @jwt_required()
    @blp.response(200, ReminderLogResponseSchema(many=True), description="List of reminder logs for a subscription.")
    @apply_common_responses(blp, RESOURCE_ERRORS)
    def get(self, sub_id: int) -> List[ReminderLogModel]:
        user_id = get_jwt_identity()
        return reminder_log_service.get_user_reminder_logs_by_subscription(sub_id, user_id)

@blp.route("/reminder_logs/<int:log_id>")
class ReminderLog(MethodView):
    @jwt_required()
    @blp.response(200, ReminderLogResponseSchema, description="Details of a specific reminder log.")
    @apply_common_responses(blp, RESOURCE_ERRORS)
    def get(self, log_id: int) -> ReminderLogModel:
        user_id = get_jwt_identity()
        return reminder_log_service.get_user_reminder_log_by_id(log_id, user_id)

    @jwt_required()
    @blp.response(200, description="Reminder log deleted successfully.")
    @apply_common_responses(blp, RESOURCE_ERRORS)
    def delete(self, log_id: int) -> dict[str, str]:
        user_id = get_jwt_identity()
        reminder_log_service.delete_reminder_log(log_id, user_id)
        return {"message": "Reminder log deleted."}