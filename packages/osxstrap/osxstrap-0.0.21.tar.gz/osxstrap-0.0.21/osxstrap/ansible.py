# -*- coding: utf-8 -*-

"""osxstrap.ansible: Ansible project creation and management for osxstrap."""

import os

import yaml

import output

import command

def install(config):
	base_install_dir = config['install_dir']
	base_install_dir = base_install_dir.replace('~', os.path.expanduser("~"))
	create_dirs(base_install_dir)
	write_yaml(os.path.join(base_install_dir, 'requirements.yml'), config['requirements'])
	create_playbooks(base_install_dir, config['playbooks'], config['dev_mode'])
	create_inventory(base_install_dir)
	create_master_playbook(base_install_dir, config['playbooks'])
	if 'extra_roles_path' in config.keys() and config['extra_roles_path']:
		extra_roles_path = ":" + config['extra_roles_path'] + ""
	else:
		extra_roles_path = ''
	create_ansible_config(base_install_dir, extra_roles_path)
	galaxy_install(base_install_dir)

def create_dirs(base_install_dir):
	mkdir(base_install_dir)
	mkdir(os.path.join(base_install_dir, 'roles'))
	mkdir(os.path.join(base_install_dir, 'playbooks'))

def mkdir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def create_ansible_config(base_install_dir, extra_roles_path):
	contents = "[defaults]\nroles_path=%s%s" % (os.path.join(base_install_dir, 'roles'), extra_roles_path)
	write_string(os.path.join(base_install_dir, 'ansible.cfg'), contents)

def create_inventory(base_install_dir):
	contents = "[all]\nlocalhost\n[all:vars]\nansible_connection=local"
	write_string(os.path.join(base_install_dir, 'inventory'), contents)

def create_playbooks(base_install_dir, playbooks, dev_mode):
	for p in playbooks:
		if not 'extra' in p.keys():
			extra = ''
		else:
			extra = p['extra']
		if dev_mode:
			role = p['dev_role']
		else:
			role = p['role']
		data = get_playbook_yaml(role, extra)
		write_yaml(os.path.join(base_install_dir, 'playbooks', p['file'] + '.yml'), data)

def create_master_playbook(base_install_dir, playbooks):
	contents = "---\n"
	for p in playbooks:
		contents += "- include: " + p['file'] + ".yml\n"
	write_string(os.path.join(base_install_dir, 'playbooks', 'all.yml'), contents)

def get_playbook_yaml(role, extra=''):
	string = "- hosts: all\n  roles:\n    - role: %s\n%s" % (role, extra)
	return yaml.load(string)

def write_yaml(file_path, data, truncate=True):
	contents = yaml.dump(data)
	write_string(file_path, contents, truncate)

def write_string(file_path, contents, truncate=True):
	target = open(file_path, 'w')
	if truncate:
		target.truncate()
	target.write(contents)
	target.close()
	output.debug('Wrote to file %s' % file_path)

def galaxy_install(base_install_dir):
	command.run('ansible-galaxy install -f -r "%s" -p "%s"' % (os.path.join(base_install_dir, 'requirements.yml'), os.path.join(base_install_dir, 'roles')))

def playbook(config, playbook='all', extras=None):
	os.environ["ANSIBLE_CONFIG"] = os.path.join(config['install_dir'], 'ansible.cfg')
	command_string = 'ansible-playbook'
	command_string += ' -i "%s"' % os.path.join(config['install_dir'], 'inventory')
	if config['ask_sudo_pass']:
		command_string += ' --ask-sudo-pass'
	if config['ask_vault_pass']:
		command_string += ' --ask-vault-pass'
	if extras:
		command_string += ' ' + extras
	command_string += ' "' + os.path.join(config['install_dir'], 'playbooks', playbook) + '.yml"'
	command.run(command_string)