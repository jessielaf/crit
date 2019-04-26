import unittest
from crit.executors.git import GitCheckoutExecutor


class CommandTest(unittest.TestCase):
    def test_command(self):
        self.assertEqual(GitCheckoutExecutor().commands(), 'git checkout master')

    def test_command_version(self):
        self.assertEqual(GitCheckoutExecutor(version='feature/test').commands(), 'git checkout feature/test')

    def test_command_force(self):
        self.assertEqual(GitCheckoutExecutor(force=True).commands(), 'git checkout --force master')
