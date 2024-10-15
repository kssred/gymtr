from importlib import import_module
from typing import Callable


def import_string(dotted_path: str) -> Callable:
    """
    Импортирует модуль/класс, путь к которому разделён точками

    :raise ImportError: В случае неудачного импорта/неверно указанного пути
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as e:
        raise ImportError from e

    try:
        module = import_module(module_path)
    except ModuleNotFoundError as e:
        raise ImportError from e

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise ImportError from e


def get_object_dotted_path(obj: object) -> str:
    """Получает путь к объекту, разделённый точками"""
    try:
        return f"{obj.__module__}.{obj.__qualname__}"
    except AttributeError:
        return f"{obj.__module__}.{obj.__class__.__name__}"
