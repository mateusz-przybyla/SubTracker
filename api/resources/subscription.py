from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.schemas import SubscriptionSchema, SubscriptionUpdateSchema
from api.services.subscription import create_subscription, get_user_subscriptions, delete_subscription, get_subscription_by_id, update_subscription

blp = Blueprint("subscription", __name__, description="Operations on subscriptions")

@blp.route("/subscription")
class SubscriptionsList(MethodView):
    @jwt_required()
    @blp.response(200, SubscriptionSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()
        return get_user_subscriptions(user_id), 200

    @jwt_required()
    @blp.arguments(SubscriptionSchema)
    @blp.response(201, SubscriptionSchema)
    def post(self, data):
        user_id = get_jwt_identity()
        return create_subscription(data, user_id), 201
    
@blp.route("/subscription/<int:sub_id>")
class Subscription(MethodView):
    @jwt_required()
    @blp.response(200, SubscriptionSchema)
    def get(self, sub_id):
        user_id = get_jwt_identity()
        return get_subscription_by_id(sub_id, user_id), 200
    
    @jwt_required()
    @blp.arguments(SubscriptionUpdateSchema)
    @blp.response(200, SubscriptionSchema)
    def put(self, update_data, sub_id):
        user_id = get_jwt_identity()
        return update_subscription(sub_id, user_id, update_data), 200
    
    @jwt_required()
    @blp.response(200, SubscriptionSchema)
    def delete(self, sub_id):
        user_id = get_jwt_identity()
        delete_subscription(sub_id, user_id)
        return {"message": "Subscription deleted."}, 200
