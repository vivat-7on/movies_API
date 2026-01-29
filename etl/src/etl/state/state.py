import datetime

from etl.state.storage import JsonFileStorage


class State:
    def __init__(self, storage: JsonFileStorage):
        self.storage = storage
        self._state: dict = self.storage.load()

    def get(self, name_ts: str) -> datetime.datetime | None:
        value = self._state.get(name_ts)
        if value is None:
            return None
        return datetime.datetime.fromisoformat(value)

    def set(self, key: str, value: datetime.datetime | None) -> None:
        if value is None:
            self._state.pop(key, None)
        else:
            self._state[key] = value.isoformat()
        self.storage.save(self._state)
