# ReminderLog exceptions

class ReminderLogCreateError(Exception): pass
class ReminderLogDeleteError(Exception): pass 
class ReminderLogNotFoundError(Exception): pass

# Subscription exceptions

class SubscriptionCreateError(Exception): pass
class SubscriptionUpdateError(Exception): pass
class SubscriptionDeleteError(Exception): pass
class SubscriptionNotFoundError(Exception): pass
class SubscriptionExistError(Exception): pass

# Exceptions used by email providers (Mailgun, etc.)

class EmailTemporaryError(Exception): pass
class EmailPermanentError(Exception): pass