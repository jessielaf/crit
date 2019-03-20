import unittest
from crit.executors.utils import UserAddExecutor


class CommandTest(unittest.TestCase):
    base = 'useradd'
    standard = 'useradd -s /bin/bash -m'

    def test_command(self):
        self.assertEqual(UserAddExecutor(username='test').commands(), f'{self.standard} test')

    def test_command_password(self):
        self.assertEqual(UserAddExecutor(username='test', password='test').commands(), f'{self.standard} -p \'test\' test')

    def test_command_create_home(self):
        self.assertEqual(UserAddExecutor(username='test', create_home=False).commands(), f'{self.base} -s /bin/bash test')

    def test_command_shell(self):
        self.assertEqual(UserAddExecutor(username='test', shell='/bin/shell').commands(), f'{self.base} -s /bin/shell -m test')

    def test_command_groups(self):
        self.assertEqual(UserAddExecutor(username='test', groups=['test', 'test2']).commands(), f'{self.standard} -G test,test2 test')
