#!/usr/bin/env python3
# vim:syntax=python:filetype=python:ts=4:sw=4:noet:

import os, shutil, sys
from setuptools import setup


setup(
	name = 'termdraw',
	version = '0.1',
	author = 'Ilya Terentyev',
	author_email = 'bacondropped@gmail.com',
	description = 'Utility library for textual data visualization',
	license = 'MIT',
	keywords = 'data graph ascii visualization',
	url = 'https://github.com/bacondropped/termdraw',
	packages = ['termdraw'],
	scripts = ['bin/termdraw'],
	classifiers = [
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'License :: Freely Distributable',
		'Programming Language :: Python :: 3 :: Only',
		'Topic :: Scientific/Engineering :: Visualization',
		'Topic :: Utilities'
	]
)

# Install manpages
# TODO: remove manpages on uninstall
if 'install' in sys.argv and os.name is 'posix':
	man1_path = '/usr/share/man/man1/'
	man3_path = '/usr/share/man/man3/'

	if os.path.exists(man1_path):
		man1_page = 'termdraw.1'
		print('Installing ' + man1_page + ' to ' + man1_path)
		shutil.copy2(os.path.join('.', 'docs', man1_page), man1_path)
		os.chmod(os.path.join(man1_path, man1_page), int('644', 8))

	if os.path.exists(man3_path):
		man3_page = 'termdraw.3'
		print('Installing ' + man3_page + ' to ' + man3_path)
		shutil.copy2(os.path.join('.', 'docs', man3_page), man3_path)
		os.chmod(os.path.join(man3_path, man3_page), int('644', 8))
