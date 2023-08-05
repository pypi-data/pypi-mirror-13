#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse
import subprocess

XDG_CONF_DIR = os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.environ.get('HOME'), '.config')
CONF_DIR = os.path.join(XDG_CONF_DIR, 'AllTheDots')
DOT_LIST = os.path.join(CONF_DIR, 'savelist.txt')


def command_add(stuffList, paths):
	"Add paths to list of stuff"
	abs_paths = [os.path.abspath(x) for x in paths]
	confdir = os.path.dirname(stuffList)
	if not os.path.isdir(confdir):
		os.makedirs(confdir)

	with open(stuffList, 'a+') as f:
		dotlist = [s.strip() for s in f.readlines()]
		for i in abs_paths:
			parents = [s for s in dotlist if i.startswith(os.path.join(s,''))]
			if len(parents) == 0:
				f.write(i+'\n')
				print '{dotpath} added to {dotlistfile}'.format(dotpath=i, dotlistfile=stuffList)
			else:
				print '{dotlistfile} already contains {parents}'.format(dotlistfile=stuffList, parents=' and '.join(parents))


def command_backup(stuffList, target):
	"Uses rsync to make a backup of the stuff listed in the stufflist"
	subprocess.call(('rsync', '-arvPh', '--delete-delay', '--update', '--files-from', stuffList, '/', target))


def main():
	parser = argparse.ArgumentParser(description='Make a list of important stuff')
	subparsers = parser.add_subparsers(help='sub-command help')

	# add <path>
	parser_add = subparsers.add_parser('add', help=command_add.__doc__)
	parser_add.add_argument('paths', metavar='path', nargs='+', help='This file or directory is important stuff')
	parser_add.set_defaults(func=command_add, args=lambda x: (DOT_LIST, x.paths))

	# backup <to target>
	parser_backup = subparsers.add_parser('backup', help=command_backup.__doc__)
	parser_backup.add_argument('target', metavar='target', help='This can be any rsync-compatible path')
	parser_backup.set_defaults(func=command_backup, args=lambda x: (DOT_LIST, x.target))

	# parse args
	args = parser.parse_args()
	args.func(*args.args(args))
	


if __name__ == '__main__':
	main()
