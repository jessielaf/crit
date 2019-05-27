# todo: The clone mock is not working
import unittest
from unittest import mock
from crit.config import Localhost
from crit.executors.git import GitExecutor


class ExecuteTest(unittest.TestCase):
    @mock.patch('crit.executors.git.git_executor.GitCloneExecutor')
    @mock.patch('crit.executors.git.git_executor.GitCheckoutExecutor')
    @mock.patch('crit.executors.git.git_executor.GitPullExecutor')
    def test_command(self, clone, checkout, pull):
        repository = 'git@github.com:jessielaf/effe'
        version = 'develop'
        force = True
        chdir = '/test'

        executor = GitExecutor(
            repository=repository,
            version=version,
            force=force,
            chdir=chdir,
            host=Localhost()
        )

        executor.execute()

        clone.called_with(
            repository=repository,
            name=f'Cloning {repository}',
            **executor.get_base_attributes()
        )

        checkout.called_with(
            version=version,
            force=force,
            name=f'Checking out {version} for {repository}',
            **executor.get_base_attributes()
        )

        pull.called_with(
            force=force,
            name=f'Pulling {repository}',
            **executor.get_base_attributes()
        )
