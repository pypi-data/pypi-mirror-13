from setuptools import setup, find_packages

setup(
	name = 'getcite',
	version = '1.3.9',
	description = 'Pulls original sources from Westlaw and HeinOnline.org',
	author = 'Samuel Alexander',
	author_email = 'salexander2000@gmail.com',
	license = 'GPL',
	packages = find_packages(),

	install_requires = [
	'selenium>=2.48.0',
	'PyPDF>=1.13'
	],

)