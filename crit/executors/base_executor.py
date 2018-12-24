from typing import Union
import subprocess
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from crit.sequences import Sequence


@dataclass
class BaseExecutor(metaclass=ABCMeta):
    hosts: Union[str, list] = None
    sequence: Sequence = None

    @property
    @abstractmethod
    def commands(self) -> list:
        pass

    def execute(self):
        hosts = self.hosts or self.sequence.hosts
        results = {}

        if isinstance(hosts, str):
            results[hosts] = self.run_command(hosts)
        elif isinstance(hosts, list):
            for host in hosts:
                results[host] = self.run_command(host)

        print(results)

    def run_command(self, host):
        commands = []

        if host != 'localhost' and host != '127.0.0.1':
            commands = ["ssh", "%s" % host]

        ssh = subprocess.Popen(commands + self.commands,
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        return ssh.stdout.readlines()
