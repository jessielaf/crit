import unittest
from unittest.mock import patch
from crit.config import Localhost
from crit.executors import MultiExecutor, Result
from crit.executors.result import Status


@patch.multiple(MultiExecutor, __abstractmethods__=set())
def get_executor(*args, **kwargs):
    return MultiExecutor(*args, **kwargs)


class GetBaseAttributesTests(unittest.TestCase):
    attributes = {
        'host': Localhost(),
        'tags': ['tes'],
        'sudo': True,
        'register': 'test',
        'env': {'TEST': 'test'},
        'chdir': '/test'
    }

    def test_all_attributes(self):
        self.assertEqual(get_executor(**self.attributes).get_base_attributes(), self.attributes)

    def test_exclude_attribute(self):
        attributes = self.attributes
        del attributes['tags']

        self.assertEqual(get_executor(**self.attributes).get_base_attributes(['tags']), attributes)


class ResultFromExecutorTests(unittest.TestCase):
    def test_one_changed(self):
        executor = get_executor()
        executor.results = [
            Result(Status.CHANGED, message='test1'),
            Result(Status.SUCCESS, message='test2')
        ]

        self.assertEqual(executor.result_from_executor( 'test'), Result(Status.CHANGED, message='test'))

    def test_all_success(self):
        executor = get_executor()
        executor.results = [
            Result(Status.SUCCESS, message='test1'),
            Result(Status.SUCCESS, message='test2')
        ]

        self.assertEqual(executor.result_from_executor('test'), Result(Status.SUCCESS, message='test'))

    def test_all_changed(self):
        executor = get_executor()
        executor.results = [
            Result(Status.CHANGED, message='test1'),
            Result(Status.CHANGED, message='test2')
        ]

        self.assertEqual(executor.result_from_executor('test'), Result(Status.CHANGED, message='test'))
