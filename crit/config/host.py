import os
from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class Host:
    """
    Configuration for a specific host

    Args:
        url (str): The url of the host
        ssh_user (str): The user that will be used when ssh'ing into the host
        ssh_password (str): The password that will be used when ssh'ing into the host
        ssh_identity_file (str): The path to the private key
        name (str): The name that will be displayed when using the cli commands
        data (dict): Data specific for host
    """

    url: str
    ssh_user: str
    ssh_password: str = None
    ssh_identity_file: str = '~/.ssh/id_rsa'
    name: str = None
    data: dict = None

    def __repr__(self):
        return self.name or self.url


@dataclass(frozen=True, repr=False)
class Localhost(Host):
    """
    Premade configuration for localhost
    """

    url: str = '127.0.0.1'
    ssh_user: str = os.getlogin()
