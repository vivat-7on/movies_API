import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class JsonFileStorage:
    def __init__(self, file_name: str) -> None:
        self.file_name = Path(file_name)

    def save(self, data: dict) -> None:
        try:
            with open(self.file_name, "w") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                logger.debug("Saved data to %s", self.file_name)
        except Exception:
            logger.exception(
                "Failed to save data to %s",
                self.file_name,
            )
            raise

    def load(self) -> dict:
        if not self.file_name.exists():
            logger.info(
                "State file %s does not exist, starting fresh",
                self.file_name,
            )
            return {}
        try:
            with open(self.file_name, "r") as file:
                data = json.load(file)
                logger.debug("Loaded data from %s", self.file_name)
        except Exception:
            logger.exception(
                "Failed to load data to %s",
                self.file_name,
            )
            raise
        return data
