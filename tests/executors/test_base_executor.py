import unittest
from unittest.mock import patch, Mock, MagicMock
from crit.config import Localhost, config, Host
from crit.executors import Result, BaseExecutor
from crit.executors.result import Status


@patch.multiple(BaseExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return BaseExecutor(*args, **kwargs)


class RunTests(unittest.TestCase):
    def test_wrong_tags(self):
        config.tags = ['tag']
        self.assertEqual(get_executor().run(host=Localhost()), Result(Status.SKIPPING, message='Skipping based on tags'))

    def test_run(self):
        config.tags = []
        executor = get_executor()

        host = Localhost()

        has_tags = Mock()
        executor.has_tags = has_tags

        not_in_config_hosts = MagicMock(return_value=False)
        executor.not_in_config_hosts = not_in_config_hosts

        result = Result(status=Status.CHANGED)
        execute = MagicMock(return_value=result)
        executor.execute = execute

        register_result = Mock()
        executor.register_result = register_result

        result_returned = executor.run(host=host)

        self.assertTrue(has_tags.called)
        self.assertTrue(not_in_config_hosts.called)
        self.assertTrue(execute.called)

        register_result.assert_called_with(result)
        self.assertEqual(result, result_returned)

    def test_not_in_config(self):
        config.hosts = []
        executor = get_executor()
        host = Host(url='test.com', ssh_user='test')

        self.assertEqual(executor.run(host), Result(Status.SKIPPING, message='Host is not in global config or passed as argument') )

    @classmethod
    def tearDownClass(cls):
        config.tags = []


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


class InConfigHostsTest(unittest.TestCase):
    host = Host(url='test', ssh_user='test')

    def test_host_in_config(self):
        config.hosts = [self.host]
        executor = get_executor()
        executor.host = self.host

        self.assertEqual(executor.not_in_config_hosts(), None)

    def test_host_not_in_config(self):
        config.hosts = []
        executor = get_executor()
        executor.host = self.host

        self.assertEqual(executor.not_in_config_hosts(), Result(Status.SKIPPING, message='Host is not in global config or passed as argument'))

    def test_localhost(self):
        config.hosts = []
        executor = get_executor()
        executor.host = Localhost()

        self.assertEqual(executor.not_in_config_hosts(), None)

    @classmethod
    def tearDownClass(cls):
        config.hosts = []


class TagsTest(unittest.TestCase):
    """
    Tests if the right response is returned when some tags are set
    """

    def test_no_tags_no_skip_tags(self):
        config.tags = []
        config.skip_tags = []

        self.assertTrue(get_executor().has_tags())

    def test_with_tags_no_skip_no_tags_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertFalse(get_executor().has_tags())

    def test_no_tags_with_skip_no_tags_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag1']

        self.assertTrue(get_executor().has_tags())

    def test_with_tags_no_skip_tags_tags_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertTrue(get_executor(tags=['tag1', 'tag2']).has_tags())

    def test_with_tags_no_skip_tags_tags_not_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertFalse(get_executor(tags=['tag2']).has_tags())

    def test_no_tags_with_skip_tags_skip_tags_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag2']

        self.assertFalse(get_executor(tags=['tag1', 'tag2']).has_tags())

    def test_no_tags_with_skip_tags_skip_tags_not_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag2']

        self.assertTrue(get_executor(tags=['tag1']).has_tags())

    def test_tags_and_skip_tags_in_executor(self):
        """
        This test the priority of the config.tags over config.skip_tags
        """

        config.tags = ['tag1']
        config.skip_tags = ['tag1']

        self.assertTrue(get_executor(tags=['tag1']).has_tags())

    @classmethod
    def tearDownClass(cls):
        config.tags = []
        config.skip_tags = []
