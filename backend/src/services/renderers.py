from pathlib import Path

from jinja2 import Template

from src.core.config import settings
from src.templates import TemplatePath


class TemplateRenderer:
    """Класс для работы с шаблоном письма"""

    _base_path: Path = settings.BASE_DIR / "src/templates"

    @classmethod
    def render_template(cls, data: dict, template_path: TemplatePath) -> str:
        """
        Рендеринг шаблона письма в строку

        :param data: Словарь с содержанием письма
        :param template_path: Путь к файлу шаблона
        :returns: Строка с отформатированным письмом
        """

        template_file = cls._base_path / template_path
        template_file_text = template_file.read_text()
        return Template(template_file_text).render(**data)


template_renderer = TemplateRenderer()
