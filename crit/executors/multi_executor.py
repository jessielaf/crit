from abc import ABC
from dataclasses import dataclass
from typing import List
from crit.executors.result import Status
from crit.executors import BaseExecutor, Result


@dataclass
class MultiExecutor(BaseExecutor, ABC):
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

    def get_base_attributes(self, excluded=None) -> dict:
        """
        Gets the base attributes of the base executor for the nested executors. These are the available attributes that can be excluded:
            - tags
            - sudo
            - register
            - env
            - chdir

        Args:
            excluded (List[str]): attributes that should not be included in the return

        Returns:
            a dict of attributes
        """

        # The list of the attributes it should pass on from base executor
        base_attributes = [
            'host',
            'tags',
            'sudo',
            'register',
            'env',
            'chdir'
        ]

        if excluded:
            for attr in excluded:
                base_attributes.remove(attr)

        attributes = {}

        for attr in base_attributes:
            attributes[attr] = self.__getattribute__(attr)

        return attributes
