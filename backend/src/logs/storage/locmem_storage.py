import json

from src.logs.storage import LogStorageABC
from src.logs.types import LOG_KIND


class LocMemLogStorage(LogStorageABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.storage = []
        self.name = "logs"

    def append(self, kind: LOG_KIND, value) -> int:
        initial_size = len(self.storage)
        log_name = f"{kind}_{self.name}"
        log_dict = {log_name: value}
        log_json = json.dumps(log_dict)
        self.storage.append(log_json.encode("utf-8"))
        return initial_size + 1

    def get(self, kind: LOG_KIND) -> list[bytes]:
        filter_data = []
        encode_kind = kind.encode("utf-8")
        for item in self.storage:
            if encode_kind in item:
                key = json.loads(item)
                key_data = key[f"{kind}_logs"]
                json_data = json.dumps(key_data)
                filter_data.append(json_data.encode("utf-8"))
        return filter_data

    def clear(self) -> int:
        initial_size = len(self.storage)
        self.storage.clear()
        return initial_size
