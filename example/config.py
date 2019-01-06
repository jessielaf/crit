from crit.config.host import Host

slave1 = Host(url='192.168.200.101', ssh_user='vagrant', name='Slave 1')

hosts = [
    slave1
]
