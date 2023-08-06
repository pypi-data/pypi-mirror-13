#!/usr/bin/python3
from setuptools import setup

setup(
	# General description and project information
	name        = 'NetLink',
	description = 'Pure-Python client for the Linux NetLink interface',
	version     = '0.1',
	url         = 'https://xmine128.tk/Software/Python/netlink/',
	platforms   = ['Linux'],
	license     = 'LGPL-3.0+',
	classifiers = [
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Topic :: System :: Networking',
		'Topic :: System :: Networking :: Firewalls',
		'Topic :: System :: Operating System Kernels :: Linux',
	],
	
	setup_requires                     = ['setuptools-markdown'],
	long_description_markdown_filename = 'README.md',
	
	# Author information
	author       = 'Alexander Schlarb',
	author_email = 'alexander-devel@xmine128.tk',
	
	# Build information
	packages = ['netlink', 'netlink.low', 'netlink.struct'],
)
