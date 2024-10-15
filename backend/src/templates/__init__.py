from enum import StrEnum


class TemplatePath(StrEnum):
    EMAIL_PASSWORD_RESET_TXT = "email/password_reset.txt"
    EMAIL_EMAIL_VERIFY_TXT = "email/email_verify.txt"
    EMAIL_EMAIL_CHANGE_TXT = "email/email_change.txt"
