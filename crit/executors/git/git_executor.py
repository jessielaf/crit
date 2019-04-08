from dataclasses import dataclass
from crit.executors.result import Status
from crit.exceptions import SingleExecutorFailedException
from . import GitCloneExecutor, GitCheckoutExecutor, GitPullExecutor
from crit.executors import MultiExecutor, Result


@dataclass
class GitExecutor(MultiExecutor):
    """
    Executor that clones, checks out and pulls a repository

    Args:
        repository (str): The repository that will be cloned. :obj:`required`
        version (str): Version of the repository. Defaults to :obj:`'master'`
        force (bool): Force changes made in the repository to be discarded. Defaults to :obj:`False`
    """

    repository: str = ''
    version: str = ''
    force: bool = False

    def execute(self, **kwargs) -> Result:
        """

        Args:
            **kwargs (dict): The extra vars passed in the function

        Returns:
            Result from the git executors
        """

        try:
            self.execute_executor(GitCloneExecutor(
                repository=self.repository,
                name=f'Cloning {self.repository}',
                **self.get_base_attributes()
            ))

            self.execute_executor(GitCheckoutExecutor(
                version=self.version,
                force=self.force,
                name=f'Checking out {self.version} for {self.repository}',
                **self.get_base_attributes()
            ))

            self.execute_executor(GitPullExecutor(
                force=self.force,
                name=f'Pulling {self.repository}',
                **self.get_base_attributes()
            ))

            return self.result_from_executor('Updated github repository')
        except SingleExecutorFailedException as e:
            return e.result

