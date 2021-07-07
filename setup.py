from setuptools import setup, find_packages

setup(
	name='trio-pools',
	version='0.0.1',
	packages=find_packages('src/'),
	package_dir={'': 'src'},
	tests_require=['pytest', 'pytest-trio'],
	url='https://github.com/Ostoic/trio-pools',
	license='MIT',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	description=''
)
