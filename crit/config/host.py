import os
from dataclasses import dataclass


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

    url: str = 'localhost'

    # Added the try except for read the docs os.getlogin() needs permissions
    try:
        ssh_user: str = os.getlogin()
    except OSError:
        ssh_user: str = 'LOCAL USER'
