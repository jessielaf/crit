import unittest
from unittest.mock import Mock, patch
from crit.config import Localhost, config
from crit.executors import Result, BaseExecutor
from crit.executors.result import Status
from example import config as example_config
from example.test import sequence


@patch.multiple(BaseExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return BaseExecutor(*args, **kwargs)


class RunTest(unittest.TestCase):
    def test_run(self):
        run_executors = Mock()
        sequence.run_executors = run_executors

        sequence.run()

        run_executors.called_with(sequence.executors)
