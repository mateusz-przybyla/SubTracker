from flask import Flask

from api.exceptions import (
    ReminderLogNotFoundError,
    ReminderLogCreateError, 
    ReminderLogDeleteError, 
    SubscriptionNotFoundError,
    SubscriptionExistError,
    SubscriptionCreateError,
    SubscriptionUpdateError,
    SubscriptionDeleteError
)

def register_error_handlers(app: Flask):
    @app.errorhandler(ReminderLogNotFoundError)
    @app.errorhandler(SubscriptionNotFoundError)
    def handle_not_found(e):
        return {"message": str(e)}, 404

    @app.errorhandler(SubscriptionExistError)
    def handle_conflict(e):
        return {"message": str(e)}, 409

    @app.errorhandler(ReminderLogCreateError)
    @app.errorhandler(ReminderLogDeleteError)
    @app.errorhandler(SubscriptionCreateError)
    @app.errorhandler(SubscriptionUpdateError)
    @app.errorhandler(SubscriptionDeleteError)
    def handle_server_error(e):
        return {"message": str(e)}, 500