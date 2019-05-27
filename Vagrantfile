Vagrant.configure("2") do |config|
  config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1", auto_correct: true
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox"

  config.vm.provision "shell" do |s|
    ssh_pub_key = File.readlines("#{Dir.home}/.ssh/id_rsa.pub").first.strip
    s.inline = <<-SHELL
      echo #{ssh_pub_key} >> /home/vagrant/.ssh/authorized_keys
    SHELL
  end

  (1..2).each do |i|
    config.vm.define "slave#{i}" do |slave|
      slave.vm.box = "debian/stretch64"
      slave.vm.network "private_network", ip: "192.168.200.10#{i}"

      slave.vm.provider "virtualbox" do |v|
        v.memory = 256
      end
    end
  end

  config.vm.define "master" do |master|
    master.vm.network "private_network", ip: "192.168.200.100"
    master.vm.box = "ubuntu/bionic64"

    master.ssh.forward_agent = true
    master.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/id_rsa.pub"
    master.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"

    master.vm.provision "shell" do |s|
      s.inline = <<-SHELL
        sudo apt-get update
        sudo apt-get upgrade
        sudo apt-get install -y python3-setuptools python3-pip python3-sphinx
        pip3 install -r /vagrant/requirements-build.txt
        cat /home/vagrant/.ssh/id_rsa.pub >> /home/vagrant/.ssh/authorized_keys
      SHELL
    end

    master.vm.provider "virtualbox" do |v|
	    v.memory = 256
    end
  end
end
