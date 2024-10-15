from json import JSONDecodeError, loads
from typing import Any, Iterable


class PIIFilter:
    """
    Класс для замены PII в лог-записях

    :param pii_patterns: Паттерны ключей, значения которых необходимо заменить
    :param exclude_patterns: Паттерны ключей, значения которых не нужно хранить в лог-записях
    """

    def __init__(
        self, pii_patterns: Iterable[str], exclude_patterns: Iterable[str]
    ) -> None:
        self._pii_patterns = pii_patterns
        self._exclude_patterns = exclude_patterns

    def replace(self, request_data: dict[str, Any]) -> dict:
        """Удалить/заменить ненужные/чувствительные данные из лог-записи"""

        body = request_data.get("request_body", "")

        try:
            body = loads(body)
        except JSONDecodeError:
            body = self._replace_string(body)
        else:
            body = self._replace_dict(body)

        request_data["request_body"] = body
        return request_data

    def _replace_string(self, body: str) -> str:
        data = body.split("&")

        for idx, field in enumerate(data):
            try:
                key, _ = field.split("=")
            except ValueError:
                return body

            if any(pattern in key.lower() for pattern in self._exclude_patterns):
                data.pop(idx)
            elif any(pattern in key.lower() for pattern in self._pii_patterns):
                data[idx] = f"{key}=<SECURE>"

        return "&".join(data)

    def _replace_dict(self, body: dict[str, Any]) -> dict[str, Any]:
        body_copy = body.copy()
        for key in body_copy.keys():
            if any(pattern in key.lower() for pattern in self._exclude_patterns):
                body.pop(key)
            elif any(pattern in key.lower() for pattern in self._pii_patterns):
                body[key] = "<SECURE>"

        return body
