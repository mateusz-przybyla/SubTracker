from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.schemas import SubscriptionSchema, SubscriptionUpdateSchema
from api.services.subscription import create_subscription, get_user_subscriptions, delete_subscription, get_subscription_by_id, update_subscription
from api.docs.common_responses import apply_common_responses, RESOURCE_ERRORS, CREATION_ERRORS, LISTING_ERRORS

blp = Blueprint("subscription", __name__, description="Operations on subscriptions")

@blp.route("/subscription")
class SubscriptionsList(MethodView):
    @jwt_required()
    @blp.response(200, SubscriptionSchema(many=True), description="List of user subscriptions.")
    @apply_common_responses(blp, LISTING_ERRORS)
    def get(self):
        user_id = get_jwt_identity()
        return get_user_subscriptions(user_id)

    @jwt_required()
    @blp.arguments(SubscriptionSchema)
    @blp.response(201, SubscriptionSchema, description="Subscription created successfully.")
    @apply_common_responses(blp, CREATION_ERRORS)
    def post(self, data):
        user_id = get_jwt_identity()
        return create_subscription(data, user_id)
    
@blp.route("/subscription/<int:sub_id>")
class Subscription(MethodView):
    @jwt_required()
    @blp.response(200, SubscriptionSchema, description="Subscription details retrieved successfully.")
    @apply_common_responses(blp, RESOURCE_ERRORS)
    def get(self, sub_id):
        user_id = get_jwt_identity()
        return get_subscription_by_id(sub_id, user_id)
    
    @jwt_required()
    @blp.arguments(SubscriptionUpdateSchema)
    @blp.response(200, SubscriptionSchema, description="Subscription updated successfully.")
    @apply_common_responses(blp, RESOURCE_ERRORS + [(409, "Resource already exists.")])
    def put(self, update_data, sub_id):
        user_id = get_jwt_identity()
        return update_subscription(sub_id, user_id, update_data)
    
    @jwt_required()
    @blp.response(200, description="Subscription deleted successfully.")
    @apply_common_responses(blp, RESOURCE_ERRORS)
    def delete(self, sub_id):
        user_id = get_jwt_identity()
        delete_subscription(sub_id, user_id)
        return {"message": "Subscription deleted."}
