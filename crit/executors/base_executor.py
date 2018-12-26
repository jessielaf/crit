from typing import Union, List
import subprocess
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from crit.config import Host
from crit.sequences import Sequence


@dataclass
class BaseExecutor(metaclass=ABCMeta):
    hosts: Union[Host, List[Host]] = None
    sequence: Sequence = None

    @property
    @abstractmethod
    def commands(self) -> list:
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
        commands = []

        if host.url != 'localhost' and host.url != '127.0.0.1':
            commands = ["ssh", "%s" % host.url]

        ssh = subprocess.Popen(commands + self.commands,
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        return ssh.stdout.readlines()
