from distutils.core import setup

setup(
	name='TDI_DB',
	version='0.1.0',
	author='Kevin Lu',
	author_email='kevin.n.lu123@gmail.com',
	packages=['tdisql'],
	license='LICENSE.txt',
	url='http://pypi.python.org/pypi/TDI_DB/',
	description='Module for accessing the TDI SQL database through Python.',
	long_description=open('README.txt').read(),
	install_requires=['MySQL-python'],
)