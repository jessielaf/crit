from dataclasses import dataclass


@dataclass(frozen=True)
class Host:
    url: str
    ssh_user: str
    ssh_password: str = None
    ssh_identity_file = '~/.ssh/id_rsa'

    def __repr__(self):
        return self.url


@dataclass(frozen=True, repr=False)
class Localhost(Host):
    url: str = 'localhost'
    ssh_user: str = ''