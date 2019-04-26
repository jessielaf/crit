import unittest
from crit.executors.utils import FileExecutor
from crit.executors.utils.file_executor import TypeFile


class CommandTest(unittest.TestCase):
    def test_command_dir(self):
        self.assertEqual(FileExecutor(path='test', type_file=TypeFile.DIRECTORY).commands(), 'mkdir test')

    def test_command_file(self):
        self.assertEqual(FileExecutor(path='test', type_file=TypeFile.FILE).commands(), 'touch test')
