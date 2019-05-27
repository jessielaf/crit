import unittest
from crit.config import config, Localhost
from crit.executors.utils import TemplateExecutor
from crit.sequences import Sequence


class TestTemplateExecutor(unittest.TestCase):
    def test_create_template(self):
        config.registry['test'] = 'test2'
        executor = TemplateExecutor(
            src='tests/unit/helpers/template.txt',
            dest='test'
        )
        executor.sequence = Sequence(executors=[])
        executor.host = Localhost()

        self.assertEqual(executor.commands(), 'printf \'test test2 localhost\' | tee test')
