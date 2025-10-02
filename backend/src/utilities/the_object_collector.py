from types import MappingProxyType


class TheObjectCollector:
    """ storage area of object """

    _instance = None
    _data = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def addOrUpdate(cls, key, value, logger=None):
        cls._data[key] = value
        if logger:
            logger.info(f"{key} : {value} added to the object collector")

    @classmethod
    def removeKey(cls, key, logger=None):
        cls._data.pop(key, None)
        if logger:
            logger.info(f"{key} removed from the object collector")

    @classmethod
    def getDataReadOnly(cls):
        return MappingProxyType(cls._data)

    @classmethod
    def getKey(cls, key, logger=None):
        data = cls._data.get(key, None)
        if logger:
            logger.info(f"Checking for key: {key}, got data: {data}")
        return data



