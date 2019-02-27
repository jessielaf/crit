from crit.executors.result import Status

from crit.exceptions import SingleExecutorFailedException
from crit.executors.git import GitCloneExecutor, GitCheckoutExecutor, GitPullExecutor

from crit.config import Host
from crit.executors import MultiExecutor, Result


class GitExecutor(MultiExecutor):
    """
    Executor that clones, checks out and pulls a repository

    Args:
        repository (str): The repository that will be cloned. :obj:`required`
        path (str): Path to which the repository should be cloned. :obj:`required`
        version (str): Version of the repository. Defaults to :obj:`'master'`
        force (bool): Force changes made in the repository to be discarded. Defaults to :obj:`False`
        **kwargs: Everything that will be passed to the executors. :obj:`optional`
    """

    repository: str
    path: str
    version: str
    force: bool
    kwargs: dict

    def __init__(self, repository: str, path: str, version: str = 'master', force: bool = False, **kwargs):
        self.repository = repository
        self.path = path
        self.version = version
        self.force = force
        self.kwargs = kwargs

    def execute(self, host: Host, **kwargs) -> Result:
        """

        Args:
            host (Host): host on which the executor is ran
            **kwargs (dict): The extra vars passed in the function

        Returns:
            Result from the git executors
        """

        try:
            results = []

            results.append(GitCloneExecutor(
                repository=self.repository,
                name=f'Cloning {self.repository}',
                chdir=self.path,
                **self.kwargs
            ).execute(host, True))

            results.append(GitCheckoutExecutor(version=self.version, force=self.force, chdir=self.path,
                                name=f'Checking out {self.version} for {self.repository}', **self.kwargs)
                           .execute(host, True))

            results.append(GitPullExecutor(force=self.force, chdir=self.path, name=f'Pulling {self.repository}',
                                           **self.kwargs).execute(host, True))

            return self.result_from_executor(results, 'Updated github repository')
        except SingleExecutorFailedException:
            return Result(Status.FAIL, message='An executor failed')

