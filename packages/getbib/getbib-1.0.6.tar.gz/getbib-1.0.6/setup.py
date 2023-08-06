try:
	from setuptools import setup, find_packages
except:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import setup, find_packages

setup(
	name = 'getbib',
	version = '1.0.6',
	description = 'Pulls an author\'s bibliography from Westlaw.',
	author = 'Samuel Alexander',
	author_email = 'salexander2000@gmail.com',
	license = 'GPL',
	packages = ['getbib'],
	
	install_requires = [
	'selenium>=2.48.0',
	'python-docx>=0.8.5'
	],

)
