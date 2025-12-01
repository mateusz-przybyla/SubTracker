import pytest
import fakeredis
import datetime
from decimal import Decimal
from flask_jwt_extended import create_access_token

from api import create_app
from api.extensions import db
from api.models import UserModel, SubscriptionModel
from api.models.subscription import BillingCycleEnum

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session

@pytest.fixture(autouse=True)
def mock_redis(mocker):
    fake_redis = fakeredis.FakeRedis()
    mocker.patch("api.extensions.redis_client", fake_redis)
    yield fake_redis

@pytest.fixture
def sample_user(db_session):
    user = UserModel(username="test", email="test@example.com", password="secret")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def fresh_jwt(app, sample_user):
    with app.app_context():
        access_token = create_access_token(identity=str(sample_user.id), fresh=True)
        return access_token

@pytest.fixture
def jwt(app, sample_user):
    with app.app_context():
        access_token = create_access_token(identity=str(sample_user.id))
        return access_token
    
@pytest.fixture
def sample_subscription(db_session, sample_user):
    subscription = SubscriptionModel(
        name="Netflix",
        price=Decimal("29.99"),
        billing_cycle=BillingCycleEnum.monthly,
        next_payment_date=datetime.date(2025, 1, 15),
        category="entertainment",
        user_id=sample_user.id,
    )
    db_session.add(subscription)
    db_session.commit()
    return subscription