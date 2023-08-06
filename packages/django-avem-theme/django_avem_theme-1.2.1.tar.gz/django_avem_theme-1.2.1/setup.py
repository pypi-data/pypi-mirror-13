# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.rst', 'r') as fh:
	readme = fh.read()

setup(
	name='django_avem_theme',
	description='Simple bootstrap3 theme for Django',
	long_description=readme,
	url='https://github.com/mverleg/django_avem_theme',
	author='Mark V',
	maintainer='(the author)',
	author_email='mdilligaf@gmail.com',
	license='Revised BSD License (LICENSE.txt)',
	keywords=['django', 'bootstrap'],
	version='1.2.1',
	packages=['avem_theme'],
	include_package_data=True,
	zip_safe=False,
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'License :: OSI Approved :: BSD License',
	],
	install_requires=[
		'django',
	],
)


