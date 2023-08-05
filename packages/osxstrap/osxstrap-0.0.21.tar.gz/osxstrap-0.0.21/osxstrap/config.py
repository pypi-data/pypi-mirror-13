# -*- coding: utf-8 -*-

"""osxstrap.config: Parse configuration."""

import os

import yaml

import output

import ansible

user_config_keys = ['config_method','config_source','ask_sudo_pass','ask_vault_pass','extra_roles_path','install_dir', 'dev_mode']

base_path = os.path.dirname(__file__)
yaml_path = os.path.join(base_path, 'config', 'base.yml')
home_yaml_path = os.path.join(os.path.expanduser("~"), '.osxstraprc')

with open(yaml_path, 'r') as stream:
	base_config = yaml.load(stream)

if os.path.exists(home_yaml_path):
	with open(home_yaml_path, 'r') as stream:
		user_config = yaml.load(stream)
		if isinstance(user_config, dict):
			config = base_config.copy()
			config.update(user_config)
		else:
			config = base_config

else:
	config = base_config

for key in user_config_keys:
	if not key in config.keys():
		config[key] = None

if 'install_dir' in config.keys():
	config['install_dir'] = config['install_dir'].replace('~', os.path.expanduser("~"))
	
def save_user_config(config):
	user_config = dict()
	for key in user_config_keys:
		if not config[key] == None:
			user_config[key] = str(config[key])
	ansible.write_yaml(home_yaml_path, user_config)