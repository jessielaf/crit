import unittest
from crit.config import config, Localhost
from crit.executors import TemplateExecutor
from crit.sequences import Sequence


class TestTemplateExecutor(unittest.TestCase):
    def test_create_template(self):
        config.registry['test'] = 'test2'
        executor = TemplateExecutor(
            src='helpers/template.txt',
            dest='test'
        )
        executor.sequence = Sequence(executors=[])
        executor.host = Localhost()

        self.assertEqual(executor.commands(), 'echo test test2 localhost > test')


if __name__ == '__main__':
    unittest.main()
