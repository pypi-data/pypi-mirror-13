from .adapter.inmemory  import InMemory
from .adapter.exception import NotSupported
from .mixin             import DictionaryAccess

class Storage(DictionaryAccess):
    def __init__(self, driver=InMemory()):
        self.driver = driver

    def get(self, key):
        return self.driver.get(key)

    def set(self, key, value):
        self.driver.set(key, value)

    def remove(self, key):
        self.driver.remove(key)

    def find(self, *args, **kwargs):
        try:
            return self.driver.find(*args, **kwargs)
        except NotSupported as e:
            return []
