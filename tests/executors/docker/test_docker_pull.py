import unittest
from crit.executors.docker import DockerPullExecutor


class CommandTest(unittest.TestCase):
    def test_command_no_args(self):
        self.assertEqual(DockerPullExecutor(image='test').commands(), 'docker pull test')

    def test_command_registry_url(self):
        self.assertEqual(DockerPullExecutor(image='test', registry_url='test.com').commands(), 'docker pull test.com/test')

    def test_command_extra_commands(self):
        self.assertEqual(DockerPullExecutor(image='test', extra_commands='--tag tag').commands(), 'docker pull --tag tag test')
