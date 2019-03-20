import unittest
from crit.executors.git import GitCloneExecutor


class CommandTest(unittest.TestCase):
    def test_command(self):
        self.assertEqual(GitCloneExecutor(repository='git@github.com:jessielaf/effe').commands(), 'git clone git@github.com:jessielaf/effe')
