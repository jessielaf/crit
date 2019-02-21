from crit.executors.git import GitCloneExecutor, GitCheckoutExecutor, GitPullExecutor


def get_git_executors(repository: str, path: str, version: str = 'master', force: bool = False, **kwargs):
    return [
        GitCloneExecutor(repository=repository, chdir=path, name=f'Cloning {repository}', **kwargs),
        GitCheckoutExecutor(chdir=path, version=version, force=force, name=f'Checking out {version} for {repository}', **kwargs),
        GitPullExecutor(chdir=path, force=force, name=f'Pulling {repository}', **kwargs)
    ]
