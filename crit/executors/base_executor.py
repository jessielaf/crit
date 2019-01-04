import os
from typing import Union, List
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import paramiko

from crit.config import Host, config, Localhost
from crit.sequences import Sequence


@dataclass
class BaseExecutor(metaclass=ABCMeta):
    hosts: Union[Host, List[Host]] = None
    sequence: Sequence = None

    @property
    @abstractmethod
    def commands(self) -> str:
        pass

    def execute(self):
        hosts = self.hosts or self.sequence.hosts
        results = {}

        if isinstance(hosts, Host):
            results[hosts] = self.run_command(hosts)
        elif isinstance(hosts, List):
            for host in hosts:
                results[host] = self.run_command(host)

        print(results)

    def run_command(self, host: Host):
        stdin, stdout, stderr = self.get_client(host).exec_command(self.commands)

        return stdout.read().decode().split('\n')

    @staticmethod
    def get_client(host: Host):
        if host.url in config.channels:
            return config.channels[host.url]
        else:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.load_system_host_keys()
            client.connect(hostname=host.url, username=host.ssh_user, password=host.ssh_password,
                           pkey=paramiko.RSAKey.from_private_key_file(os.path.expanduser(host.ssh_identity_file)),
                           allow_agent=False, look_for_keys=False)

            config.channels[host.url] = client

            return client
