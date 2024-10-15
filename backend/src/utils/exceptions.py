from src.exceptions import ProjectException


class InvalidID(ProjectException):
    reason = "Невалидный ID"
