import unittest
from unittest.mock import Mock, patch

from crit.config import Localhost
from crit.executors import SingleExecutor, Result
from crit.executors.result import Status
from crit.sequences import Sequence


@patch.multiple(SingleExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return SingleExecutor(*args, **kwargs)


class RunTest(unittest.TestCase):
    def test_run(self):
        # Host and the empty mock
        host = Localhost()
        empty_mock = Mock()

        # Mock the result
        result = Result(Status.SUCCESS)
        result.print_line = empty_mock

        # Mock the execute function
        execute = Mock()
        execute.return_value = result

        # Mock the post execute function
        post_executors = Mock()
        post_executors.return_value = []

        # Mock the executor
        executor = get_executor()
        executor.execute = execute
        executor.post_executors = post_executors

        sequence = Sequence(
            hosts=[host],
            executors=[
                executor
            ]
        )

        sequence.print_title = empty_mock

        sequence.run()

        execute.called_with(host)
        post_executors.called_with(result)
