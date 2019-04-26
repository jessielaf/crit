import unittest
from unittest.mock import patch, Mock, MagicMock
from crit.config import Localhost, config, Host
from crit.executors import Result, BaseExecutor
from crit.executors.result import Status


@patch.multiple(BaseExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return BaseExecutor(*args, **kwargs)


class RunTests(unittest.TestCase):
    def test_run(self):
        config.tags = []
        host = Localhost()

        executor = get_executor()
        executor.host = host

        not_in_config_hosts = MagicMock(return_value=False)
        executor.not_in_config_hosts = not_in_config_hosts

        result = Result(status=Status.CHANGED)
        execute = MagicMock(return_value=result)
        executor.execute = execute

        register_result = Mock()
        executor.register_result = register_result

        executor.run()

        self.assertTrue(not_in_config_hosts.called)
        self.assertTrue(execute.called)

        register_result.assert_called_with()
        self.assertEqual(result, executor.result)

    def test_not_in_config(self):
        config.hosts = []
        host = Host(url='test.com', ssh_user='test')
        executor = get_executor()
        executor.host = host

        self.assertEqual(executor.run(), Result(Status.SKIPPING, message='Host is not in global config or passed as argument') )

    @classmethod
    def tearDownClass(cls):
        config.tags = []


class RegisterResultTest(unittest.TestCase):
    def test_register_result(self):
        executor = get_executor(register='test')
        result = Result(Status.CHANGED, 'test', ['test'])
        host = Localhost()

        executor.host = host
        executor.result = result

        executor.register_result()

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
