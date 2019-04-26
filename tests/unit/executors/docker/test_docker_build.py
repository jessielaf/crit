import unittest
from crit.executors.docker import DockerBuildExecutor


class CommandTest(unittest.TestCase):
    def test_command_no_args(self):
        self.assertEqual(DockerBuildExecutor().commands(), 'docker build .')

    def test_command_tag(self):
        self.assertEqual(DockerBuildExecutor(tag='test').commands(), 'docker build --tag test .')

    def test_command_memory(self):
        self.assertEqual(DockerBuildExecutor(memory='5gb').commands(), 'docker build --memory 5gb .')
