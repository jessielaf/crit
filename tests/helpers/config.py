from crit.config import Host, GeneralConfig

config = GeneralConfig(
    hosts=[
        Host('192.168.200.101', ssh_user='vagrant'),
        Host('192.168.200.102', ssh_user='vagrant'),
        Host('192.168.200.103', ssh_user='vagrant'),
    ]
)
