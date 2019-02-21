import shutil

from dataclasses import dataclass
from typing import Union, List, Callable

from termcolor import colored

from crit.config import config, Host
from crit.executors import BaseExecutor


@dataclass
class Sequence:
    """
    The sequence that will be ran by the cli command

    Args:
        executors (List[Union[BaseExecutor, Callable[[], List[BaseExecutor]]]]): The executors that will be ran in the same order as this list. This list can also contain a function that returns executors. This is because you can than use runtime variables. :obj:`required`
        hosts (Union[Host, List[Host]]): The hosts on which this sequence will run. :obj:`optional`

    Attributes:
        term_width (int): Width of the terminal
    """

    executors: List[Union[BaseExecutor, Callable[[Host], List[BaseExecutor]]]]
    hosts: Union[Host, List[Host]] = None

    term_width = shutil.get_terminal_size((80, 20)).columns - 1

    def run(self):
        """
        Runs all the executors in this sequence and closes all the channels of the hosts after running the executors
        """
        self.hosts = self.hosts or config.hosts

        self.run_executors(self.executors)

        for name, channel in config.channels.items():
            channel.close()

    def run_executors(self, executors: List[BaseExecutor]):
        """
        Runs all the executors in an array on every host

        Args:
            executors (List[BaseExecutor]): The executors to run
        """

        for executor in executors:
            for host in self.hosts:
                if isinstance(executor, BaseExecutor):
                    self.print_title(executor)
                    self.run_executor(host, executor)
                else:
                    new_executors = executor(host)

                    if new_executors:
                        for new_executor in new_executors:
                            self.print_title(new_executor)
                            self.run_executor(host, new_executor)

    def run_executor(self, host: Host, executor: BaseExecutor):
        """
        Run an executor on a host. Also runs the nested executors with :obj:`run_command`

        Args:
            host (Host): Host on which the executor will run
            executor (BaseExecutor): Executor that will run
        """

        result = executor.execute(host)
        result.to_table(host)

        self.run_executors(executor.post_executors(result))

    def print_title(self, executor):
        """
        Prints the title of the executor in the commandline
        """

        if len(config.hosts) != 0:
            line = '=' * self.term_width

            print('\n')
            print(line)
            print(colored(executor.name or executor.__class__.__name__, attrs=['bold']))
            print(line)
