import unittest

from .cache import Cache

class StandardTests(unittest.TestCase):
    def get_driver(self):
        return None

    def ready_driver(self):
        pass

    def kill_driver(self):
        pass

    def setUp(self):
        self.driver = self.get_driver()
        self.ready_driver()

        if not self.driver:
            raise unittest.SkipTest('The driver is not defined.')

        self.cache = Cache(self.driver)

    def tearDown(self):
        self.kill_driver()

        del self.cache
        del self.driver

    def test_set_and_get(self):
        self.cache.set('panda', 'something')
        self.assertEqual('something', self.cache.get('panda'))

    def test_set_twice(self):
        self.cache.set('panda', 'something')
        self.assertEqual('something', self.cache.get('panda'))

        self.cache.set('panda', 'python')
        self.assertEqual('python', self.cache.get('panda'))

    def test_get_nothing(self):
        self.assertEqual(None, self.cache.get('panda'))

    def test_remove_once(self):
        self.cache.set('panda', 'something')
        self.cache.remove('panda')

        self.assertEqual(None, self.cache.get('panda'))

    def test_remove_once(self):
        self.cache.set('panda', 'something')
        self.cache.remove('panda')
        self.cache.remove('panda') # ensure that there is no error.

        self.assertEqual(None, self.cache.get('panda'))

    def test_dictionary_access(self):
        self.cache['panda'] = 'something'
        self.assertEqual('something', self.cache['panda'])
