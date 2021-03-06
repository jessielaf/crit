import unittest
from io import BytesIO
from unittest import mock
from unittest.mock import patch, Mock
from crit.config import Localhost, config, Host
from crit.exceptions import SingleExecutorFailedException
from crit.executors import SingleExecutor, Result
from crit.executors.result import Status


@patch.multiple(SingleExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return SingleExecutor(*args, **kwargs)


class ExecuteOnHostTest(unittest.TestCase):
    """
    Tests if the output paramiko returns is parsed correctly
    """

    host = Localhost()
    result = Result(Status.SUCCESS)

    def test_execute_success(self):
        executor = self.mock_executor()
        result = executor.execute()

        self.assertEqual(result, self.result)

    def test_throw_exception_on_fail(self):
        self.result = Result(status=Status.FAIL)
        executor = self.mock_executor()

        with self.assertRaises(SingleExecutorFailedException):
            executor.execute(True)

    def mock_executor(self, **kwargs):
        # Set executor
        executor = get_executor(**kwargs)

        # Mock run_command() on executor
        run_command_mock = Mock()
        run_command_mock.return_value = self.result
        executor.run_command = run_command_mock

        return executor

    def setUp(self):
        config.hosts = [self.host]


class RunCommandTest(unittest.TestCase):
    @mock.patch('paramiko.SSHClient')
    def test_execute_on_host_success(self, client_mock):
        executor = self.mock_executor(client_mock, (BytesIO(b'output'), BytesIO(b'output'), BytesIO(b'')))

        result = executor.run_command()

        self.assertEqual(result.status, Status.SUCCESS)

    @mock.patch('paramiko.SSHClient')
    def test_execute_on_host_success_sudo(self, client_mock):
        # mock ssh client
        executor = self.mock_executor(client_mock, (BytesIO(b'output'), BytesIO(b'output'), BytesIO(b'')), sudo=True)

        fill_password = Mock()
        fill_password.return_value = None
        executor.fill_password = fill_password

        result = executor.run_command()

        self.assertEqual('sudo value', result.stdin)

    @mock.patch('paramiko.SSHClient')
    def test_execute_warning(self, client_mock):
        executor = self.mock_executor(client_mock, (BytesIO(b'warnings'),) * 3)

        result = executor.run_command()
        self.assertEqual(result.status, Status.SUCCESS)

    @mock.patch('paramiko.SSHClient')
    def test_chdir(self, client_mock):
        executor = self.mock_executor(client_mock, (BytesIO(b'warnings'),) * 3, chdir='/var/www')

        result = executor.run_command()
        self.assertEqual(result.stdin, 'cd /var/www && value')

    @mock.patch('paramiko.SSHClient')
    def test_env_variables(self, client_mock):
        executor = self.mock_executor(client_mock, (BytesIO(b'warnings'),) * 3, env={'TEST': 'test1'})

        result = executor.run_command()
        self.assertEqual(result.stdin, 'TEST="test1" value')

    @mock.patch('paramiko.SSHClient')
    def test_execute_warning_error(self, client_mock):
        executor = self.mock_executor(client_mock, (BytesIO(b'warnings error'),) * 3)

        result = executor.run_command()
        self.assertEqual(result.status, Status.FAIL)

    @mock.patch('paramiko.SSHClient')
    def test_execute_error(self, client_mock):
        executor = self.mock_executor(client_mock, (BytesIO(b'error'),) * 3)

        result = executor.run_command()
        self.assertEqual(result.status, Status.FAIL)

    @mock.patch('paramiko.SSHClient')
    def test_execute_wrong_password(self, client_mock):
        executor = self.mock_executor(client_mock, (BytesIO(b'output'),) * 3)

        fill_password = Mock()
        fill_password.return_value = Result(Status.FAIL, message='Incorrect linux password!')
        executor.fill_password = fill_password

        result = executor.run_command()
        self.assertEqual(result, Result(Status.FAIL, message='Incorrect linux password!'))

    def mock_executor(self, client_mock, exec_return, **kwargs):
        # Set executor
        executor = get_executor(**kwargs)
        executor.host = Localhost()

        # Mock commands() on executor
        commands_mock = Mock()
        commands_mock.return_value = 'value'
        executor.commands = commands_mock

        # Mock get_client on executor
        client_mock.return_value.exec_command.return_value = exec_return
        executor.get_client = client_mock

        return executor

    def setUp(self):
        config.hosts = [Localhost()]
        config.registry = {}


class FillPasswordTest(unittest.TestCase):
    @mock.patch('paramiko.ChannelFile')
    def test_no_sudo(self, channel):
        self.assertEqual(get_executor().fill_password('', channel), None)

    @mock.patch('paramiko.ChannelFile')
    def test_sudoless_user(self, channel):
        executor = get_executor()

        host = Host('test.url', 'jessie', passwordless_user=True)
        executor.host = host

        self.assertEqual(executor.fill_password(channel, channel), None)

    @mock.patch('paramiko.ChannelFile')
    def test_no_linux_password(self, channel):
        executor = get_executor(sudo=True)
        config.linux_password = ''

        host = Host('test.url', 'jessie')
        executor.host = host

        self.assertEqual(executor.fill_password(channel, channel), Result(Status.FAIL, message='Pass linux password with -p or pass passwordless_user on hosts!'))

    @mock.patch('paramiko.ChannelFile')
    def test_right_password(self, channel):
        executor = get_executor(sudo=True)
        config.linux_password = 'test'

        readline = Mock()
        readline.return_value = ''
        channel.readline = readline
        channel.write = Mock()

        host = Host('test.url', 'jessie')
        executor.host = host

        self.assertEqual(executor.fill_password(channel, channel), None)

    @mock.patch('paramiko.ChannelFile')
    def test_wrong_password(self, channel):
        executor = get_executor(sudo=True)
        config.linux_password = 'test'

        readline = Mock()
        readline.return_value = 'Sorry, try again.'
        channel.readline = readline
        channel.write = Mock()

        host = Host('test.url', 'jessie')
        executor.host = host

        self.assertEqual(executor.fill_password(channel, channel), Result(Status.FAIL, message='Incorrect linux password!'))
