import unittest
from unittest.mock import Mock, patch

from crit.config import Localhost, config
from crit.executors import Result
from crit.executors.result import Status
from crit.executors.utils import CommandExecutor
from crit.sequences import Sequence


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

        # Mock the executor
        executor = CommandExecutor('ls')
        executor.execute = execute

        # Mock thread behaviour
        join = Mock()
        start = Mock()
        executor.start = start
        executor.join = join

        sequence = Sequence(
            hosts=[host],
            executors=[
                executor
            ]
        )

        sequence.print_title = empty_mock

        sequence.run()

        execute.called_with()
        join.called_with()
        start.called_with()
