from flask import Flask
from dotenv import load_dotenv

from api.config import Config
from api.extensions import api, jwt, db, migrate, email_queue, reminder_queue
from api.resources import ALL_BLUEPRINTS
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

    for blp in ALL_BLUEPRINTS:
        api.register_blueprint(blp)

    app.email_queue = email_queue
    app.reminder_queue = reminder_queue

    return app