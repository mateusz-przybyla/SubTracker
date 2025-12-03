from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.schemas import StatsSummarySchema, StatsSummaryQueryArgsSchema
from api.services import subscription as subscription_service

blp = Blueprint("statistic", __name__, description="Operations on subscription statistics")

@blp.route("/stats/summary")
class StatsSummary(MethodView):
    @jwt_required()
    @blp.arguments(StatsSummaryQueryArgsSchema, location="query")
    @blp.response(200, StatsSummarySchema, description="Monthly spending summary")
    def get(self, query_args: dict[str, str]) -> dict[str, object]:
        """Retrieve a summary of monthly subscription spending."""
        user_id = get_jwt_identity()
        month = query_args.get("month")
        return subscription_service.get_monthly_summary(user_id, month)