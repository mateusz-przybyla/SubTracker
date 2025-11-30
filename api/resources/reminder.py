from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import List

from api.schemas import SubscriptionSchema, UpcomingQueryArgsSchema
from api.models import SubscriptionModel
from api.services import subscription as subscription_service

blp = Blueprint("reminder", __name__, description="Operations on reminders")

@blp.route("/reminders/upcoming")
class RemindersList(MethodView):
    @jwt_required()
    @blp.arguments(UpcomingQueryArgsSchema, location="query")
    @blp.response(200, SubscriptionSchema(many=True), description="List of user upcoming payments for subscriptions.")
    def get(self, query_args: dict[str, int]) -> List[SubscriptionModel]:
        user_id = get_jwt_identity()
        days = query_args['days']
        return subscription_service.get_user_upcoming_within(user_id, days)