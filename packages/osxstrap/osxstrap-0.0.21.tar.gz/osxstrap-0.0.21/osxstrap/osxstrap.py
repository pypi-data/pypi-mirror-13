# -*- coding: utf-8 -*-

"""osxstrap.osxstrap: provides entry point main()."""


__version__ = "0.0.21"


import os

import click

import shutil

import command

import output

import ansible

from config import config, save_user_config, user_config_keys


overwrite_conflicting = False

skip_conflicting = False


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--playbook', '-p', default='all', help='Playbook to run.')
def cli(ctx, playbook):
    if ctx.invoked_subcommand is None:
    	ansible.playbook(config, playbook)

@cli.command()
@click.option('--install-dir', '-d', default=False, help='Where to install the osxstrap Ansible project.')
@click.option('--config-method', '-c', default=False, help='Where to get config from. Can be local_path, remote_file, or git_repo.')
@click.option('--config-source', '-s', default=False, help='Config source (either a remote URL or local path).')
@click.option('--ask-sudo-pass', '-k', default=None, is_flag=True, help='Have Ansible prompt you for a sudo password.')
@click.option('--ask-vault-pass', '-v', default=None, is_flag=True, help='Have Ansible prompt you for a vault password.')
@click.option('--dev-mode', '-dev', default=False, is_flag=True, help='Install in development mode.')
@click.option('--extra-roles-path', '-p', default=None, help='Additional path to look for Ansible roles (useful for development).')
def install(install_dir, config_method, config_source, ask_sudo_pass, ask_vault_pass, dev_mode, extra_roles_path):
	output.running('Starting install.')
	if not install_dir:
		install_dir = click.prompt('Install directory path', default=config['install_dir'])
	config['install_dir'] = install_dir
	if not config_method and not config['config_method']:
		config['config_method'] = get_config_method()
	if not config_source and not config['config_source']:
		config['config_source'] = get_config_source(config['config_method'])
	if ask_sudo_pass == None and config['ask_sudo_pass'] == None:
		if click.confirm('Do you want to have Ansible prompt you for a sudo password (set to yes if you do not have passwordless sudo)?'):
			config['ask_sudo_pass'] = True
		else:
			config['ask_sudo_pass'] = False
	if ask_vault_pass == None and config['ask_vault_pass'] == None:
		if click.confirm('Do you want to have Ansible prompt you for a vault password (set to yes if you are using vault)?'):
			config['ask_vault_pass'] = True
		else:
			config['ask_vault_pass'] = False
	if extra_roles_path:
		config['extra_roles_path'] = extra_roles_path
	config['dev_mode'] = dev_mode
	save_user_config(config)
	ansible.install(config)

def get_config_method():
	response = click.prompt('Enter a config type. Can be local_path, remote_file, or git_repo')
	if response not in ['local_path','remote_file','git_repo']:
		output.waring('Invalid input.')
		return get_config_method()
	else:
		return response

def get_config_source(method):
	if method == 'local_path':
		prompt = 'Enter the path to local a local file or directory to load config from'
	elif method == 'remote_file':
		prompt = 'Enter the URL of the remote file to load config from'
	elif method == 'git_repo':
		prompt = 'Enter the URL of the git repo to clone and load config from'
	else:
		output.about('Invalid config method: %s' % method)
	response = click.prompt(prompt)
	return response

@cli.group()
def conf():
    pass

@conf.command()
def list():
	for k in user_config_keys:
		output.debug('%s = %s' % (key, config[k]))

@conf.command()
@click.option('--key', '-k', default=None, required=True, help='Key to look up.')
def get(key):
	for k in user_config_keys:
		if key == k:
			output.debug('%s = %s' % (key, config[key]))


@conf.command()
@click.option('--key', '-k', default=None, required=True, help='Key to set.')
@click.option('--value', '-v', default=None, required=True, help='Value to set.')
def set(key, value):
	if key in user_config_keys:
		config[key] = value
		save_user_config(config)
	output.debug('Set %s to %s' % (key, value))
