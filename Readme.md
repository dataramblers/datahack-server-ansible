_This script may not follow best practices. We still learning ansible_
# Datahack (SAH) Server ansible script
This small ansible playbook setup a Server for the SAH Datahack. It installs docker and starts two containers: One container serves the IIIF image API and one a nginx reverse proxy. The playbook downloads the SAH images from the [data.stadt-zuerich.ch](https://data.stadt-zuerich.ch/dataset/sozialarchiv-sah) and mounts them into the loris container.
## Install 
```bash
# install python-pip
apt-get install python-pip
# install ansible
pip install ansible
# clone repo
git clone https://github.com/dataramblers/datahack-server-ansible.git
# get required ansible roles
ansible-galaxy install geerlingguy.pip
ansible-galaxy install geerlingguy.docker
```
## Features
* The playbook will install [docker](https://www.docker.com/) on the target system
* The playbook will configure a loris docker container ([lorisimageserver/loris](https://hub.docker.com/r/lorisimageserver/loris/))
* The playbook will configure a elastic search container ([docker.elastic.co/elasticsearch/elasticsearch:6.2.2](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html))
* The playbook will configure a reverse proxy ([jwilder/nginx-proxy](bbtsoftwareag/nginx-proxy-unrestricted-requestsize:alpine))
* The playbook downloads the sah images from [data.stadt-zuerich.ch](https://data.stadt-zuerich.ch/dataset/sozialarchiv-sah) and mount it into the loris container 
* The playbook will download the sah metadata and stream it to ES

## Requirement
You need some sort of target system. That might be a droplet on digital ocean or a virtual machine. On this machine you need a user with sudo rights. A usual method to deploy with ansible is to add a user ansible on the target system and add it to the sudoers f.e. [/etc/sudoers.d/ansible](https://github.com/dataramblers/datahack-server-ansible/blob/master/ansible.security.target.hosts.txt)
.
 ```bash
 adduser ansible
 echo "ansible ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/ansible
 ```
## configuration
You can set several variables in the inventory to control the playbook. See also the [ansible docu](http://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#list-of-behavioral-inventory-parameters) for more 
* data: This is the place to store the image data from the sah 
* domain: This domain is used in the setup of the reverse proxy

## Use locally (untested)
You could use the script against your local system, but this is a bad idea. It tries to restart your system and will install some packages you don't really need.
```
# filename: local
[local]
localhost    ansible_user=YOURUSER  ansible_connection=local data=./data domain=dataramblers.localhost
``` 

Then you can start the script 
```
ansible-playbook -i local playbook.yml
```
## Deploy 
Install a debian based linux distribution in a hypervisor (f.e. (virtualbox)[https://www.virtualbox.org/]). For this example we used ubuntu 16.04 server edition. You need to enable openssh-server and configure a user with sudo rights. Before you start take a snapshot of your machine. so you can go back if it fails.

Configure an inventory file for the deployment to a virtualbox. This is a bit a more complex example with user password. For security reasons you should use ssh-keys or [ansible vault](https://docs.ansible.com/ansible/2.4/vault.html). You can also use the --ask-pass and --ask-become-pass parameters to manually enter the passwords.
```yaml
# filename: virtualbox.yml
test:
  hosts:
    192.168.100.11
  vars:
    ansible_ssh_pass: YOURPASSWORD
    ansible_become: True
    ansible_become_pass: YOURPASSWORD
    ansible_user: ansible
    ansible_connection: ssh
    data: /data
    domain: dataramblers.localhost
  ``` 
```bash
ansible-playbook -i virtualbox.yml playbook.yml
```

## troubleshooting
It can happen that ansible loose the connection to the target, while the target preform a reboot. This is necessary after kernel updates. If so, just rerun the script after a minute and you will be fine. Otherwise just open an issue