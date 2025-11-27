# ReminderLog errors

class ReminderLogCreateError(Exception): pass
class ReminderLogDeleteError(Exception): pass 
class ReminderLogNotFoundError(Exception): pass

# Subscription errors

class SubscriptionCreateError(Exception): pass
class SubscriptionUpdateError(Exception): pass
class SubscriptionDeleteError(Exception): pass
class SubscriptionNotFoundError(Exception): pass
class SubscriptionExistError(Exception): pass