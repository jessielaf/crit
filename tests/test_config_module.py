import unittest
from unittest.mock import patch
from crit.config import config, Localhost
from crit.executors import BaseExecutor, Result
from crit.executors.result import Status


@patch.multiple(BaseExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return BaseExecutor(*args, **kwargs)


class GetRegisteredTest(unittest.TestCase):
    def test_get_register(self):
        result = Result(Status.CHANGED)

        executor = get_executor(register='test')
        executor.host = Localhost()
        executor.result = result
        executor.register_result()

        self.assertEqual(config.get_registered(Localhost(), 'test'), result)
