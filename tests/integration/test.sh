echo Local setup
crit sequences/local_setup.py -vvv

echo Service server setup
crit sequences/service_server.py -vvv

echo Server setup
crit sequences/server_setup.py -h 192.168.200.102 -vvv

echo Deploy project
crit sequences/deploy_project.py -h 192.168.200.102 -vvv
