import os
from hvac import Client

from crit.config.general_config import GeneralConfig
from crit.config.host import Host

from hosts.slave1 import slave1

slave2 = Host(url='192.168.200.102', ssh_user='vagrant', name='slave2', passwordless_user=True)

config = GeneralConfig(
    hosts=[slave1, slave2]
)
