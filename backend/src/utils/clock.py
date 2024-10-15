from datetime import datetime, timezone


class Clock:
    """Класс-обёртка над datetime"""

    @staticmethod
    def utc_now_with_tz() -> datetime:
        """Получить текущее UTC время с информацией о timezone"""

        return datetime.now(timezone.utc)

    @staticmethod
    def utc_from_timestamp_with_tz(timestamp: float) -> datetime:
        """Получить UTC время из timestamp объекта с информацией о timezone"""

        return datetime.fromtimestamp(timestamp, timezone.utc)

    @classmethod
    def utc_now(cls) -> datetime:
        """Получить текущее UTC время без информации о timezone"""

        return cls.utc_now_with_tz().replace(tzinfo=None)

    @classmethod
    def utc_from_timestamp(cls, timestamp: float) -> datetime:
        """Получить UTC время из timestamp объекта без информации о timezone"""

        return cls.utc_from_timestamp_with_tz(timestamp).replace(tzinfo=None)

    @staticmethod
    def utc_from_datetime_with_tz(datetime_: datetime) -> datetime:
        """Получить UTC время из объекта datetime с информацией о timezone"""

        if datetime_.tzinfo:
            return datetime_.astimezone(timezone.utc)
        return datetime_

    @staticmethod
    def utc_from_datetime(datetime_: datetime) -> datetime:
        """Получить UTC время из объекта datetime без информации о timezone"""

        if datetime_.tzinfo:
            return datetime_.astimezone(timezone.utc).replace(tzinfo=None)
        return datetime_
