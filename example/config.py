from crit.config.host import Host

slave1 = Host(url='192.168.200.101', ssh_user='vagrant', ssh_identity_file='/c/Users/Jessie/.ssh/id_rsa')

hosts = [
    slave1
]
