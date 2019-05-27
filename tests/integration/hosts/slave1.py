from crit.config import Host

slave1 = Host(
    url='192.168.200.101',
    ssh_user='vagrant',
    name='slave1',
    passwordless_user=True
)