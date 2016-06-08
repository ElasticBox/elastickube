import os

TEMPLATE_PATH = os.path.dirname(os.path.abspath(__file__))

NOTIFICATIONS_SUBJECT = u"[ElasticKube] Notifications for {} - {} updates in {} namespaces"

with open(os.path.join(TEMPLATE_PATH, 'notifications.html')) as notifications_file:
    NOTIFICATIONS_TEMPLATE = notifications_file.read()
