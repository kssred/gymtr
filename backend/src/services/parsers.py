from typing import Iterable, Optional
from urllib.parse import parse_qs, quote, unquote, urlparse


class URLParser:
    @classmethod
    def quote_url(cls, text: str) -> str:
        return quote(text, safe="")

    @classmethod
    def unquote_url(cls, text: str) -> str:
        return unquote(text)

    @classmethod
    def get_query_params(
        cls, url: str, params: Iterable[str]
    ) -> dict[str, Optional[list[str]]]:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        query_params_values = {}
        for param in params:
            query_params_values[param] = query_params.get(param)

        return query_params_values
