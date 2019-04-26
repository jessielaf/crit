import shutil
from copy import deepcopy
from dataclasses import dataclass
from typing import Union, List
from crit.exceptions import NotBaseExecutorTypeException
from termcolor import colored
from crit.config import config, Host
from crit.executors import BaseExecutor, Result
from crit.executors.result import Status
from crit.sequences.thread_executor import ThreadExecutor


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

    executors: List[BaseExecutor]
    hosts: Union[Host, List[Host]] = None

    term_width = shutil.get_terminal_size((80, 20)).columns - 1

    def run(self):
        """
        Runs all the executors in this sequence and closes all the channels of the hosts after running the executors
        """
        self.hosts = self.hosts or config.hosts

        self.run_executors()

        for name, channel in config.channels.items():
            channel.close()

    def run_executors(self):
        """
        Runs all the executors in an array on every host
        """
        running_threads = []

        for executor in self.executors:
            if not self.has_tags(executor):
                if config.verbose <= 3:
                    self.print_title(executor)

                    Result(Status.SKIPPING, message='Skipping based on tags').to_table()

                continue

            self.print_title(executor)

            hosts = executor.hosts or self.hosts
            for host in hosts:
                executor = deepcopy(executor)
                if isinstance(executor, BaseExecutor):
                    executor.host = host

                    thread = ThreadExecutor(executor)
                    thread.start()

                    running_threads.append(thread)
                else:
                    raise NotBaseExecutorTypeException()

            for running_executor in running_threads:
                result = running_executor.join()

                if result:
                    result.to_table(running_executor.executor.host)

            running_threads = []

    def has_tags(self, executor: BaseExecutor) -> bool:
        """
        Check if the executor can run based on the tags.
        It prefers tags over skiptags

        Returns:
            If the executor can run or not
        """

        if config.tags:
            if not executor.tags:
                return False

            in_tags = [tag for tag in executor.tags if tag in config.tags]

            return len(in_tags) > 0
        elif config.skip_tags:
            if not executor.tags:
                return True

            in_skip_tags = [tag for tag in executor.tags if tag in config.skip_tags]

            return len(in_skip_tags) == 0

        return True

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
