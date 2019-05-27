import unittest
from unittest.mock import Mock, patch
from crit.config import Localhost, config
from crit.executors import Result, BaseExecutor
from crit.executors.result import Status
from crit.executors.utils import CommandExecutor
from crit.sequences import Sequence


@patch.multiple(BaseExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return BaseExecutor(*args, **kwargs)


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


class TagsTest(unittest.TestCase):
    """
    Tests if the right response is returned when some tags are set
    """
    sequence = Sequence(executors=[])

    def test_no_tags_no_skip_tags(self):
        config.tags = []
        config.skip_tags = []

        self.assertTrue(self.sequence.has_tags(get_executor()))

    def test_with_tags_no_skip_no_tags_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertFalse(self.sequence.has_tags(get_executor()))

    def test_no_tags_with_skip_no_tags_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag1']

        self.assertTrue(self.sequence.has_tags(get_executor()))

    def test_with_tags_no_skip_tags_tags_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertTrue(self.sequence.has_tags(get_executor(tags=['tag1', 'tag2'])))

    def test_with_tags_no_skip_tags_tags_not_in_executor(self):
        config.tags = ['tag1']
        config.skip_tags = []

        self.assertFalse(self.sequence.has_tags(get_executor(tags=['tag2'])))

    def test_no_tags_with_skip_tags_skip_tags_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag2']

        self.assertFalse(self.sequence.has_tags(get_executor(tags=['tag1', 'tag2'])))

    def test_no_tags_with_skip_tags_skip_tags_not_in_executor(self):
        config.tags = []
        config.skip_tags = ['tag2']

        self.assertTrue(self.sequence.has_tags(get_executor(tags=['tag1'])))

    def test_tags_and_skip_tags_in_executor(self):
        """
        This test the priority of the config.tags over config.skip_tags
        """

        config.tags = ['tag1']
        config.skip_tags = ['tag1']

        self.assertTrue(self.sequence.has_tags(get_executor(tags=['tag1'])))

    @classmethod
    def tearDownClass(cls):
        config.tags = []
        config.skip_tags = []
