import unittest
from io import BytesIO
from unittest import mock
from unittest.mock import patch, Mock
from crit.config import Localhost, config
from crit.executors import BaseExecutor, Result
from crit.executors.result import Status
from example.config import config as general_config


@patch.multiple(BaseExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return BaseExecutor(*args, **kwargs)


class ExecuteOnHostTest(unittest.TestCase):
    """
    Tests if the output paramiko returns is parsed correctly
    """

    host = Localhost()
    result = Result(Status.SUCCESS)

    def test_execute_success(self):
        self.mock_executor()
        result = self.executor.execute(self.host)

        self.assertEqual(result, self.result)

    def test_execute_wrong_host(self):
        self.mock_executor()
        result = self.executor.execute(general_config.hosts[0])

        self.assertEqual(result, Result(Status.SKIPPING, message='Host is not in global config or passed as argument'))

    def test_execute_no_tags(self):
        self.mock_executor()

        # Mock can run tags
        can_run_tags_mock = Mock()
        can_run_tags_mock.return_value = False
        self.executor.can_run_tags = can_run_tags_mock

        result = self.executor.execute(self.host)

        self.assertEqual(result, Result(Status.SKIPPING, message='Skipping based on tags for this host'))

    def test_execute_host_not_in_executor(self):
        self.mock_executor(hosts=[general_config.hosts[0]])

        result = self.executor.execute(self.host)

        self.assertEqual(result, Result(Status.SKIPPING, message='Host not in executor\'s host'))

    def mock_executor(self, **kwargs):
        # Set executor
        self.executor = get_executor(**kwargs)

        # Mock run_command() on executor
        run_command_mock = Mock()
        run_command_mock.return_value = self.result
        self.executor.run_command = run_command_mock

    def setUp(self):
        config.hosts = [self.host]
        print()


class RunCommandTest(unittest.TestCase):
    @mock.patch('paramiko.SSHClient')
    def test_execute_on_host_error(self, client_mock):
        self.mock_executor(client_mock, (BytesIO(b'output'),) * 3)

        result = self.executor.run_command()
        self.assertEqual(result.status, Status.FAIL)

    @mock.patch('paramiko.SSHClient')
    def test_execute_on_host_success(self, client_mock):
        self.mock_executor(client_mock, (BytesIO(b'output'), BytesIO(b'output'), BytesIO(b'')))

        result = self.executor.run_command()

        self.assertEqual(result.status, Status.SUCCESS)

    @mock.patch('paramiko.SSHClient')
    def test_execute_on_host_success_sudo(self, client_mock):
        # mock ssh client
        self.mock_executor(client_mock, (BytesIO(b'output'), BytesIO(b'output'), BytesIO(b'')), sudo=True)

        result = self.executor.run_command()

        self.assertEqual('sudo value', result.stdin)

    @mock.patch('paramiko.SSHClient')
    def test_execute_warning(self, client_mock):
        self.mock_executor(client_mock, (BytesIO(b'warnings'),) * 3)

        result = self.executor.run_command()
        self.assertEqual(result.status, Status.SUCCESS)

    @mock.patch('paramiko.SSHClient')
    def test_execute_warning_error(self, client_mock):
        self.mock_executor(client_mock, (BytesIO(b'warnings error'),) * 3)

        result = self.executor.run_command()
        self.assertEqual(result.status, Status.FAIL)

    @mock.patch('paramiko.SSHClient')
    def test_execute_error(self, client_mock):
        self.mock_executor(client_mock, (BytesIO(b'error'),) * 3)

        result = self.executor.run_command()
        self.assertEqual(result.status, Status.FAIL)

    def mock_executor(self, client_mock, exec_return, **kwargs):
        # Set executor
        self.executor = get_executor(**kwargs)
        self.executor.host = Localhost()

        # Mock commands() on executor
        commands_mock = Mock()
        commands_mock.return_value = 'value'
        self.executor.commands = commands_mock

        # Mock get_client on executor
        client_mock.return_value.exec_command.return_value = exec_return
        self.executor.get_client = client_mock

    def setUp(self):
        config.hosts = [Localhost()]

class RegisterResultTest(unittest.TestCase):
    def test_register_result(self):
        executor = get_executor(register='test')
        result = Result(Status.CHANGED, 'test', ['test'])
        host = Localhost()

        executor.host = host

        executor.register_result(result)

        self.assertEqual(config.registry[repr(host)]['test'], result)

    @classmethod
    def tearDownClass(cls):
        config.registry = {}


class TagsTest(unittest.TestCase):
    """
    Tests if the right response is returned when some tags are set
    """

    def test_no_tags_no_skip_tags(self):
        config.tags = []
        config.skip_tags = []

        self.assertTrue(get_executor().can_run_tags())

    def test_with_tags_no_skip_no_tags_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertFalse(get_executor().can_run_tags())

    def test_no_tags_with_skip_no_tags_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag1']

        self.assertTrue(get_executor().can_run_tags())

    def test_with_tags_no_skip_tags_tags_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertTrue(get_executor(tags=['tag1', 'tag2']).can_run_tags())

    def test_with_tags_no_skip_tags_tags_not_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertFalse(get_executor(tags=['tag2']).can_run_tags())

    def test_no_tags_with_skip_tags_skip_tags_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag2']

        self.assertFalse(get_executor(tags=['tag1', 'tag2']).can_run_tags())

    def test_no_tags_with_skip_tags_skip_tags_not_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag2']

        self.assertTrue(get_executor(tags=['tag1']).can_run_tags())

    def test_tags_and_skip_tags_in_executor(self):
        """
        This test the priority of the config.tags over config.skip_tags
        """

        config.tags = ['tag1']
        config.skip_tags = ['tag1']

        self.assertTrue(get_executor(tags=['tag1']).can_run_tags())

if __name__ == '__main__':
    unittest.main()
