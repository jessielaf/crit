import unittest
from crit.executors.git import GitPullExecutor


class CommandTest(unittest.TestCase):
    def test_command(self):
        self.assertEqual(GitPullExecutor().commands(), 'git pull')

    def test_command_force(self):
        self.assertEqual(GitPullExecutor(force=True).commands(), 'git --force pull')
