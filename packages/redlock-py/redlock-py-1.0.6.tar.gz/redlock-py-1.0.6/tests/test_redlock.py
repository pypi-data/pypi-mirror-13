import unittest

from redlock import Redlock


class TestRedlock(unittest.TestCase):

    def setUp(self):
        self.redlock = Redlock([{"host": "localhost"}])

    def test_lock(self):
        lock = self.redlock.lock("pants", 100)
        self.assertEqual(lock.resource, "pants")
        self.redlock.unlock(lock)
        lock = self.redlock.lock("pants", 10)
        self.redlock.unlock(lock)

    def test_blocked(self):
        lock = self.redlock.lock("pants", 1000)
        bad = self.redlock.lock("pants", 10)
        self.assertFalse(bad)
        self.redlock.unlock(lock)

    def test_bad_connection_info(self):
        with self.assertRaises(Warning):
            Redlock([{"cat": "hog"}])

    def test_py3_compatible_encoding(self):
        lock = self.redlock.lock("pants", 1000)
        key = self.redlock.servers[0].get("pants")
        self.assertEquals(lock.key, key)

