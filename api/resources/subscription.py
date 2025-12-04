from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import List

from api.schemas import SubscriptionSchema, SubscriptionUpdateSchema
from api.models import SubscriptionModel
from api.services import subscription as subscription_service
from api.docs.common_responses import apply_common_responses, RESOURCE_ERRORS, CREATION_ERRORS, LISTING_ERRORS

blp = Blueprint("subscription", __name__, description="Endpoints for managing user subscriptions")

@blp.route("/subscriptions")
class SubscriptionsList(MethodView):
    @jwt_required()
    @blp.response(200, SubscriptionSchema(many=True), description="List of user subscriptions.")
    @apply_common_responses(blp, LISTING_ERRORS)
    def get(self) -> List[SubscriptionModel]:
        user_id = get_jwt_identity()
        return subscription_service.get_user_subscriptions(user_id)

    @jwt_required()
    @blp.arguments(SubscriptionSchema)
    @blp.response(201, SubscriptionSchema, description="Subscription created successfully.")
    @apply_common_responses(blp, CREATION_ERRORS)
    def post(self, data: dict) -> SubscriptionModel:
        user_id = get_jwt_identity()
        return subscription_service.create_subscription(data, user_id)
    
@blp.route("/subscriptions/<int:sub_id>")
class Subscription(MethodView):
    @jwt_required()
    @blp.response(200, SubscriptionSchema, description="Subscription details retrieved successfully.")
    @apply_common_responses(blp, RESOURCE_ERRORS)
    def get(self, sub_id: int) -> SubscriptionModel:
        user_id = get_jwt_identity()
        return subscription_service.get_subscription_by_id(sub_id, user_id)
    
    @jwt_required()
    @blp.arguments(SubscriptionUpdateSchema)
    @blp.response(200, SubscriptionSchema, description="Subscription updated successfully.")
    @apply_common_responses(blp, RESOURCE_ERRORS + [(409, "Resource already exists.")])
    def put(self, update_data: dict, sub_id: int) -> SubscriptionModel:
        user_id = get_jwt_identity()
        return subscription_service.update_subscription(sub_id, user_id, update_data)
    
    @jwt_required()
    @blp.response(200, description="Subscription deleted successfully.")
    @apply_common_responses(blp, RESOURCE_ERRORS)
    def delete(self, sub_id: int) -> dict[str, str]:
        user_id = get_jwt_identity()
        subscription_service.delete_subscription(sub_id, user_id)
        return {"message": "Subscription deleted."}