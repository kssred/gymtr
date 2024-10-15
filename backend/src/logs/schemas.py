from typing import Optional, Union

from pydantic import BaseModel, ConfigDict


class BaseJSONLogSchema(BaseModel):
    """Схема основного тела лога в формате JSON"""

    thread: Optional[Union[int, str]]
    level: int
    level_name: str
    message: str
    source: str
    timestamp: str
    duration: Union[int, float]
    app_name: str
    app_env: Optional[str] = None
    exceptions: Optional[Union[list[str], str]] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_id: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class RequestJSONLogSchema(BaseModel):
    """Схема части запросов-ответов лога в формате JSON"""

    request_uri: str
    request_referer: str
    request_protocol: str
    request_method: str
    request_path: str
    request_host: str
    request_size: int
    request_content_type: str
    request_headers: dict[str, str]
    request_body: str
    request_direction: str
    remote_ip: str
    response_status_code: int
    response_size: int
    response_headers: dict[str, str]
    response_body: str
    duration: int
