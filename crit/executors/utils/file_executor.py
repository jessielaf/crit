from enum import Enum
from typing import List

from dataclasses import dataclass
from crit.executors import SingleExecutor


class TypeFile(Enum):
    """
    Type of files that can be passed to the :obj:`FileExecutor`
    """

    DIRECTORY = 'mkdir'
    FILE = 'touch'


@dataclass
class FileExecutor(SingleExecutor):
    """
    Create file or directory

    Args:
        path (str): The path where the file should be placed. :obj:`required`
        type_file (TypeFile): The type of the file. Directory or File. :obj:`required`
    """

    path: str = ''
    type_file: TypeFile = None

    def commands(self):
        return f'{self.type_file.value} {self.path}'

    def catched_error(self, output: List[str]):
        for line in output:
            if self.type_file == TypeFile.DIRECTORY and 'File exists' in line:
                return True

        return super().catched_error(output)
