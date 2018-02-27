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
## Usage
Configure an inventory file for the deployment
```
# filename: production
[production]
iiif.dataramblers.io
``` 
Happy deploying
```
ansible-playbook -i production playbook.yml
```