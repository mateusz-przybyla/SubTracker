from api.resources.test import blp as TestBlueprint
from api.resources.user import blp as UserBlueprint
from api.resources.subscription import blp as SubscriptionBlueprint
from api.resources.reminder_log import blp as ReminderLogBlueprint
from api.resources.reminder import blp as ReminderBlueprint
from api.resources.statistic import blp as StatisticBlueprint

ALL_BLUEPRINTS = [
    TestBlueprint,
    UserBlueprint,
    SubscriptionBlueprint,
    ReminderLogBlueprint,
    ReminderBlueprint,
    StatisticBlueprint,
]