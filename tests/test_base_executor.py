import unittest
import builtins
from io import BytesIO
from unittest import mock
from unittest.mock import patch, Mock
from crit.config import Localhost, config
from crit.executors import BaseExecutor, Result


@patch.multiple(BaseExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return BaseExecutor(*args, **kwargs)


class ExecuteOnHostTest(unittest.TestCase):
    """
    Tests if the output paramiko returns is parsed correctly
    """

    host = Localhost()
    result = Result('input', ['output'], True)

    def test_execute_on_host_host_not_in_config(self):
        config.all_hosts = []

        self.mock_executor()
        self.executor.execute_on_host(self.host)
        self.executor.run_command.assert_not_called()

    def test_execute_on_host_nested_executors(self):
        nested_executor = get_executor()
        nested_executor.execute_on_host = Mock()

        self.mock_executor('SUCCESS', executors=[nested_executor])

        self.executor.execute_on_host(self.host)
        self.executor.register_result.assert_called_with(self.host, self.result)
        nested_executor.execute_on_host.assert_called_with(self.host)

    def test_execute_on_host_nested_executors_wrong_status(self):
        nested_executor = get_executor()
        nested_executor.execute_on_host = Mock()

        self.mock_executor('CHANGED', executors=[nested_executor], status_nested_executors='FAIL')

        self.executor.execute_on_host(self.host)
        nested_executor.execute_on_host.assert_not_called()

    def mock_executor(self, status='SUCCESS', **kwargs):
        # Set executor
        self.executor = get_executor(**kwargs)

        # Mock register_result
        register_result = Mock()
        self.executor.register_result = register_result

        # Mock run_command() on executor
        run_command = Mock()
        run_command.return_value = self.result
        self.executor.run_command = run_command

        # Mock output_to_table() on executor
        output_to_table_mock = Mock()
        output_to_table_mock.return_value = 'SUCCESS'
        self.executor.output_to_table = output_to_table_mock

    def setUp(self):
        config.all_hosts = [self.host]


class RunCommandTest(unittest.TestCase):
    @mock.patch('paramiko.SSHClient')
    def test_execute_on_host_error(self, client_mock):
        # mock ssh client
        self.mock_executor(client_mock, (BytesIO(b'output'),) * 3)

        result = self.executor.run_command(Localhost())
        self.assertFalse(result.success)

    @mock.patch('paramiko.SSHClient')
    def test_execute_on_host_success(self, client_mock):
        # mock ssh client
        self.mock_executor(client_mock, (BytesIO(b'output'), BytesIO(b'output'), BytesIO(b'')))

        result = self.executor.run_command(Localhost())

        self.assertTrue(result.success)

    @mock.patch('paramiko.SSHClient')
    def test_execute_on_host_success_sudo(self, client_mock):
        # mock ssh client
        self.mock_executor(client_mock, (BytesIO(b'output'), BytesIO(b'output'), BytesIO(b'')), sudo=True)

        result = self.executor.run_command(Localhost())

        self.assertEqual('sudo value', result.stdin)

    def mock_executor(self, client_mock, exec_return, **kwargs):
        # Set executor
        self.executor = get_executor(**kwargs)

        # Mock commands() on executor
        commands_mock = Mock()
        commands_mock.return_value = 'value'
        self.executor.commands = commands_mock

        # Mock get_client on executor
        client_mock.return_value.exec_command.return_value = exec_return
        self.executor.get_client = client_mock

    def setUp(self):
        config.all_hosts = [Localhost()]


class OutputToTableTest(unittest.TestCase):
    """
    Tests if the output of the command is parsed correctly to display in cli
    """

    host = Localhost()

    def test_output_to_table_success(self):
        self.assertEqual('SUCCESS', get_executor().output_to_table(self.host, Result('value', ['Test output'], True)))

    def test_output_to_table_changed(self):
        executor = get_executor()
        changed_function = Mock()
        changed_function.return_value = True
        executor.changed = changed_function

        self.assertEqual('CHANGED', executor.output_to_table(self.host, Result('value', ['Test output'], True)))

    def test_output_to_table_fail(self):
        self.assertEqual('FAIL', get_executor().output_to_table(self.host, Result('value', ['Test output'], False)))

    def test_output_to_table_warning(self):
        """
        Tests if the error contains warning. This means that it was warning not a error
        """

        self.assertEqual('SUCCESS', get_executor().output_to_table(self.host, Result('value', ['Test warning'], False)))

    def test_output_to_table_error(self):
        """
        Tests if the error contains warning. This means that it was warning not a error
        """

        self.assertEqual('FAIL', get_executor().output_to_table(self.host, Result('value', ['Test warning error'], False)))

    @classmethod
    def setUpClass(cls):
        """
        Overwrite print because it is annoying to see it in the console
        """

        builtins.print = cls.overwrite_print

    def setUp(self):
        config.all_hosts.append(self.host)

    def overwrite_print(self, *args, **kwargs):
        pass


class IsStatusTest(unittest.TestCase):
    def is_status_true(self):
        self.assertTrue(get_executor().is_status(['test error'], 'error'))

    def is_status_false(self):
        self.assertTrue(get_executor().is_status(['test error'], 'warning'))


class RegisterResultTest(unittest.TestCase):
    def test_register_result(self):
        executor = get_executor(register='test')
        result = Result('test', ['test'], True)
        host = Localhost()

        executor.register_result(host, result)

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
