import unittest
from crit.executors.docker import DockerPushExecutor


class CommandTest(unittest.TestCase):
    def test_command(self):
        self.assertEqual(DockerPushExecutor(registry_url='test.com/test').commands(), 'docker push test.com/test')
