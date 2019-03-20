import unittest
from crit.executors.docker import DockerTagExecutor


class CommandTest(unittest.TestCase):
    def test_command(self):
        self.assertEqual(DockerTagExecutor(tag='test', registry_url='test.com/test').commands(), 'docker tag test test.com/test')
