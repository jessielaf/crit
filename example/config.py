import os
from hvac import Client

from crit.config.general_config import GeneralConfig
from crit.config.host import Host

slave1 = Host(url='192.168.200.101', ssh_user='vagrant', name='Slave 1')

config = GeneralConfig(
    [slave1],
    vault=Client(url='localhost', token=os.environ['VAULT_TOKEN'])
)
