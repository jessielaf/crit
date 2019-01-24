from typing import List
from crit.executors import CommandExecutor, AptExecutor, BaseExecutor


def get_vault_executors() -> List[BaseExecutor]:
    """

    Args:
        host: host on which vault should be installed

    Returns:
        executors that install vault
    """

    default_kwargs = {'tags': ['vault']}
    packages_required = ['unzip', 'libcap2-bin']

    executors = [
        CommandExecutor(
            name='Download vault',
            command='wget https://releases.hashicorp.com/vault/0.9.5/vault_0.9.5_linux_amd64.zip',
            never_fail=True,
            **default_kwargs
        ),
        CommandExecutor(
            name='Download vault hash',
            command='wget https://releases.hashicorp.com/vault/0.9.5/vault_0.9.5_SHA256SUMS',
            never_fail=True,
            **default_kwargs
        ),
        CommandExecutor(
            name='Check if hash equals downloaded file',
            command='grep linux_amd64 vault_*_SHA256SUMS | sha256sum -c -',
            **default_kwargs
        ),
        CommandExecutor(
            name='Update all packages',
            command='sudo apt-get update',
            **default_kwargs
        )
    ]

    for package in packages_required:
        executors.append(AptExecutor( name='Install ' + package, package=package, **default_kwargs))

    executors += [
        CommandExecutor(
            name='Unzip the vault package',
            command='unzip vault_*.zip',
            **default_kwargs
        ),
        CommandExecutor(
            name='Copy the vault package to local bin',
            command='sudo cp vault /usr/local/bin/',
            **default_kwargs
        ),
        CommandExecutor(
            name='Set capabilities for vault',
            command='sudo setcap cap_ipc_lock=+ep /usr/local/bin/vault',
            **default_kwargs
        ),
        CommandExecutor(
            name='Enable key value for vault',
            command='vault secrets enable -version 2 kv',
            **default_kwargs
        )
    ]

    return executors
