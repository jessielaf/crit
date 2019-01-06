import unittest
from io import BytesIO
from unittest import mock
from unittest.mock import patch, Mock
from termcolor import colored
from crit.config import Localhost
from crit.executors import BaseExecutor


@patch.multiple(BaseExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return BaseExecutor(*args, **kwargs)


class RunCommandTests(unittest.TestCase):
    """
    Tests if the output paramiko returns is parsed correctly
    """

    @mock.patch('paramiko.SSHClient')
    def test_run_command_error(self, client_mock):
        # mock ssh client
        self.mock_executor(client_mock, (BytesIO(b'output'),) * 3)

        self.executor.run_command(Localhost())
        self.output_to_table_mock.assert_called_with(Localhost(), ['output'], False)

    @mock.patch('paramiko.SSHClient')
    def test_run_command_success(self, client_mock):
        # mock ssh client
        self.mock_executor(client_mock, (BytesIO(b'output'), BytesIO(b'output'), BytesIO(b'')))

        self.executor.run_command(Localhost())
        self.output_to_table_mock.assert_called_with(Localhost(), ['output'], True)

    def mock_executor(self, client_mock, exec_return):
        client_mock.return_value.exec_command.return_value = exec_return
        self.executor = get_executor()
        self.executor.get_client = client_mock

        # Mock output_to_table
        self.output_to_table_mock = Mock()
        self.executor.output_to_table = self.output_to_table_mock


class OutputToTableTest(unittest.TestCase):
    """
    Tests if the output of the command is parsed correctly to display in cli
    """

    def test_output_to_table_success_no_output(self):
        host, status, output = get_executor().output_to_table(Localhost(), 'Test output', True)

        self.assertEqual(colored('localhost', 'green'), host)
        self.assertEqual('', output)
        self.assertEqual(colored('SUCCESS', 'green'), status)

    def test_output_to_table_success_with_output(self):
        host, status, output = get_executor(output=True).output_to_table(Localhost(), 'Test output', True)

        self.assertEqual(colored('localhost', 'green'), host)
        self.assertEqual(colored('Test output', 'green'), output)
        self.assertEqual(colored('SUCCESS', 'green'), status)

    def test_output_to_table_fail_no_output(self):
        host, status, output = get_executor().output_to_table(Localhost(), 'Test output', False)

        self.assertEqual(colored('localhost', 'red'), host)
        self.assertEqual(colored('Test output', 'red'), output)
        self.assertEqual(colored('FAIL', 'red'), status)
