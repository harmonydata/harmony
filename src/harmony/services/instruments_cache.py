from typing import List

from harmony.schemas.requests.text import Instrument
from harmony.util.singleton_meta import SingletonMeta


class InstrumentsCache(metaclass=SingletonMeta):
    """
    This class is responsible for caching instruments (Singleton class)
    """

    def __init__(self):
        self.__cache: dict[str, List[Instrument]] = {}

        self.__load()

    def __load(self):
        """Load cache"""

        self.__cache = {}

    def set(self, key: str, value: List[Instrument]):
        """Set key value pair"""

        self.__cache[key] = value

    def get(self, key: str) -> List[Instrument]:
        """Get value by key"""

        return self.__cache.get(key)

    def has(self, key: str) -> bool:
        """Check if key is in cache"""

        return key in self.__cache

    def get_all(self) -> dict[str, List[Instrument]]:
        """Get the whole cache"""

        return self.__cache
