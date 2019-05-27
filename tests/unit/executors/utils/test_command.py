import unittest
from crit.executors.utils import CommandExecutor


class CommandTest(unittest.TestCase):
    def test_command(self):
        self.assertEqual(CommandExecutor(command='test').commands(), 'test')
