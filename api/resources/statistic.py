from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.schemas import StatsSummaryResponseSchema, StatsSummaryQueryArgsSchema
from api.services import subscription as subscription_service
from api.docs.common_responses import apply_common_responses, LISTING_ERRORS

blp = Blueprint("statistic", __name__, description="Endpoints for generating monthly spending summaries and subscription statistics")

@blp.route("/stats/summary")
class StatsSummary(MethodView):
    @jwt_required()
    @blp.arguments(StatsSummaryQueryArgsSchema, location="query")
    @blp.response(200, StatsSummaryResponseSchema, description="Monthly spending summary")
    @apply_common_responses(blp, LISTING_ERRORS)
    def get(self, query_args: dict[str, str]) -> dict[str, object]:
        """Retrieve a summary of monthly subscription spending."""
        user_id = get_jwt_identity()
        month = query_args.get("month")
        return subscription_service.get_monthly_summary(user_id, month)