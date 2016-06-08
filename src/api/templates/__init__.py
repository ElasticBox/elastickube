import os

TEMPLATE_PATH = os.path.dirname(os.path.abspath(__file__))

INVITE_SUBJECT = u"You've been invited to ElasticKube"
RESET_PASSWORD_EMAIL_SUBJECT = u"Reset your password"
NOTIFICATIONS_SUBJECT = u"[ElasticKube] Notifications for {} - {} updates in {} namespaces"

with open(os.path.join(TEMPLATE_PATH, 'invite.html')) as invite_file:
    INVITE_TEMPLATE = invite_file.read()

with open(os.path.join(TEMPLATE_PATH, 'reset_password_email.html')) as reset_password_email_file:
    RESET_PASSWORD_EMAIL_TEMPLATE = reset_password_email_file.read()

with open(os.path.join(TEMPLATE_PATH, 'notifications.html')) as notifications_file:
    NOTIFICATIONS_TEMPLATE = notifications_file.read()
