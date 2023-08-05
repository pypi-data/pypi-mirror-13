from distutils.core import setup 

setup(
	name = 'TowelStuff664',
	version = '0.1.0', 
	author = "Bill the Bob", 
	author_email = "mike@yahoo.com",
	packages = ['towelstuff664', 'towelstuff664.test'],
	scripts = ['bin/stowe-towels.py', 'bin/wash-towels.py'],
	ursl = 'http://pypi.python.org/pypi/TowelStuff/',
	license = 'LICENSE.txt', 
	description = 'Useful towel-related stuff.',
	long_description = open('README.txt').read(),
	install_requires = [
		"Django >= 1.1.1", 
		"caldav == 0.1.4", 
		], 
)