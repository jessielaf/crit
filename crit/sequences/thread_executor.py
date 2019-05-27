from threading import Thread

from crit.executors import Result, BaseExecutor


class ThreadExecutor(Thread):
    executor: BaseExecutor = None
    _result: Result = None

    def __init__(self, executor: BaseExecutor, *args, **kargs):
        super().__init__(*args, **kargs)
        self.executor = executor

    def run(self):
        self.executor.run()
        self._result = self.executor.result

    def join(self, *args) -> Result:
        """
        Overwrite the thread join to return the result of the executor
        """

        Thread.join(self, *args)
        return self._result
