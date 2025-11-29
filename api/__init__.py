from flask import Flask
from dotenv import load_dotenv

from api.config import Config
from api.extensions import api, jwt, db, migrate, email_queue, reminder_queue
from api.resources.test import blp as TestBlueprint
from api.resources.user import blp as UserBlueprint
from api.resources.subscription import blp as SubscriptionBlueprint
from api.resources.reminder_log import blp as ReminderLogBlueprint
from api import jwt_callbacks
from api.error_handlers import register_error_handlers

def create_app(test_config=None):
    app = Flask(__name__)
    load_dotenv()

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)

    register_error_handlers(app)

    api.register_blueprint(TestBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(SubscriptionBlueprint)
    api.register_blueprint(ReminderLogBlueprint)

    app.email_queue = email_queue
    app.reminder_queue = reminder_queue

    return app