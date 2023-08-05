#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='Eve-Statsd',
    version='0.0.2',
    description='Statsd integration for eve',
    long_description=(
        open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read()),
    license=open('LICENSE.txt').read(),
    author='Salton Massally',
    author_email='salton.massally@gmail.com',
    url='https://github.com/tarzan0820/eve-statsd',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['eve', 'statsd'],
    test_suite='nose.collector',
    tests_require=['nose', 'statsdmock'],
    keywords = ['monitoring', 'logging', 'eve', 'statsd'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
