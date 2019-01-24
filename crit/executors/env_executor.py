import re
from dataclasses import dataclass
from termcolor import colored
from crit.executors import BaseExecutor


@dataclass
class EnvExecutor(BaseExecutor):
    """
    Add a environment variable

    Args:
        key (str): Key of the environment variable :obj:`required`
        value (str): Value of the environment variable :obj:`required`
        warning (bool): If the key is not all caps and split by _ warn the user or not. :obj:`optional`
    """

    key: str = ''
    value: str = ''
    warning: bool = True

    pattern = re.compile('^([A-Z]+_*)*$')

    def commands(self, host) -> str:
        if not self.pattern.match(self.key) and self.warning:
            print(colored('Key does not equal the right regex ENV_VARIABLE. To disable this message set warning to False', 'red'))

        return 'export ' + self.key + '="' + self.value + '"'
