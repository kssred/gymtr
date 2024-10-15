from typing import Optional


class ProjectException(Exception):
    reason = "Ошибка проекта"

    def __init__(self, reason: Optional[str] = None, *args, **kwargs):
        if reason:
            self.reason = reason

        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.reason


class ErrorFieldsMixin:
    error_fields: Optional[list[str]]

    def __init__(self, *args, error_fields: list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.error_fields = error_fields
