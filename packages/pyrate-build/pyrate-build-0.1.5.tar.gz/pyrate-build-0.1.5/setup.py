#!/usr/bin/env python
import os
from setuptools import setup, find_packages

dn = os.path.dirname(__file__)
version_expr = filter(lambda x: x.startswith('pyrate_version'), open(os.path.join(dn, 'pyrate.py')).readlines())
version = str.join('.', map(str, eval(version_expr[0].split('=')[-1])))

setup(
	name='pyrate-build',
	version=version,
	description='A small python based build file generator targeting ninja',
	long_description=open(os.path.join(dn, 'README.rst')).read(),
	url='https://github.com/pyrate-build/pyrate-build',
	download_url = 'https://github.com/pyrate-build/pyrate-build/tarball/' + version,
	author='Fred Stober',
	author_email='fred.stober@gmx.de',
	license='License :: OSI Approved :: Apache Software License',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: Apache Software License',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
	],

	# What does your project relate to?
	keywords='ninja build development',
	py_modules=["pyrate"],
	entry_points={
		'console_scripts': [
			'pyrate=pyrate:main',
		],
	},
)
