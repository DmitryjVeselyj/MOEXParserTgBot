from abc import ABC, abstractmethod


class BaseLoader(ABC):
    def __init__(self, db_path) -> None:
        super().__init__()
        self._db_path = db_path

