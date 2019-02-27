from abc import ABCMeta
from typing import List

from build.lib.crit.executors.result import Status
from crit.executors import BaseExecutor, Result


class MultiExecutor(BaseExecutor, metaclass=ABCMeta):
    """
    Executor interface for an executor that runs multiple executors itself as one executor
    """

    def result_from_executor(self, results: List[Result], message: str):
        """
        Gets the result for the executors

        Args:
            results (List[Result]): The results of the multiple executors run
            message (str): Success message that will be shown in the terminal

        Returns:
            Returns a result that is :obj:`Status.CHANGED` or :obj:`Status.SUCCESS`
        """

        is_changed = [result for result in results if result.status == Status.CHANGED]

        return Result(Status.CHANGED if is_changed else Status.SUCCESS, message=message)
