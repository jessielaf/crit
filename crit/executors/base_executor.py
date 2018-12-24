from __future__ import annotations
import subprocess
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from crit.sequences import Sequence


@dataclass
class BaseExecutor(metaclass=ABCMeta):
    host: str = None
    sequence: Sequence = None

    @property
    @abstractmethod
    def commands(self) -> list:
        pass

    def execute(self):
        host = self.host if self.host else self.sequence.host

        commands = []
        if host != 'localhost' and host != '127.0.0.1':
            commands = ["ssh", "%s" % host]

        ssh = subprocess.Popen(commands + self.commands,
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()

        print(result)
