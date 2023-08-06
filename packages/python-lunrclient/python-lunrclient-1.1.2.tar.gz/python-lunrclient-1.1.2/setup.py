#!/usr/bin/python

from setuptools import setup, find_packages

from lunrclient import version

setup(
    name='python-lunrclient',
    version=version.version,
    description='LunrClient',
    license='Apache License (2.0)',
    author='Derrick J Wippler',
    author_email='thrawn01@gmail.com',
    url='rackspace.com',
    packages=find_packages(exclude=['test']),
    test_suite='nose.collector',
    install_requires=['requests', 'prettytable>=0.7'],
    entry_points={
        'console_scripts': ['storage = lunrclient.storage_shell:main',
                            'lunr = lunrclient.lunr_shell:main']
    }
)
