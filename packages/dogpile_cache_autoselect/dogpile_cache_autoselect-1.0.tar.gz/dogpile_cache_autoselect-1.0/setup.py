# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.rst', 'r') as fh:
	readme = fh.read()

setup(
	name='dogpile_cache_autoselect',
	description='Simple script that attempts to automatically select an available cache backend for dogpile.cache',
	long_description=readme,
	url='https://bitbucket.org/mverleg/dogpile.cache.autoselect',
	author='Mark V',
	maintainer='(the author)',
	author_email='markv.nl.dev@gmail.com',
	license='Public domain',
	keywords=['cache',],
	version='1.0',
	packages=['dogpile_cache_autoselect'],
	include_package_data=True,
	zip_safe=True,
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	install_requires=[
		'dogpile.cache',
	],
)
