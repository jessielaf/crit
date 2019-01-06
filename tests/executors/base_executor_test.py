import unittest
from unittest.mock import patch

from termcolor import colored

from crit.config import Localhost, config
from crit.executors import BaseExecutor


class BaseExecutorTest(unittest.TestCase):
    def test_get_client_existing(self):
        config.channels = []

        client = self.get_executor().get_client(Localhost())


    def test_output_to_table_success_no_output(self):
        host, status, output = self.get_executor().output_to_table(Localhost(), 'Test output', True)

        self.assertEqual(colored('localhost', 'green'), host)
        self.assertEqual('', output)
        self.assertEqual(colored('SUCCESS', 'green'), status)

    def test_output_to_table_success_with_output(self):
        host, status, output = self.get_executor(output=True).output_to_table(Localhost(), 'Test output', True)

        self.assertEqual(colored('localhost', 'green'), host)
        self.assertEqual(colored('Test output', 'green'), output)
        self.assertEqual(colored('SUCCESS', 'green'), status)

    def test_output_to_table_fail_no_output(self):
        host, status, output = self.get_executor().output_to_table(Localhost(), 'Test output', False)

        self.assertEqual(colored('localhost', 'red'), host)
        self.assertEqual(colored('Test output', 'red'), output)
        self.assertEqual(colored('FAIL', 'red'), status)

    @patch.multiple(BaseExecutor, __abstractmethods__=set())
    def get_executor(self, *args, **kwargs):
        return BaseExecutor(*args, **kwargs)
