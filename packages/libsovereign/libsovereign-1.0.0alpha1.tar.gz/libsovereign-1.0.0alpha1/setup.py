import os
import sys
from distutils.sysconfig import get_python_lib

from setuptools import find_packages, setup

EXCLUDE_FROM_PACKAGES = []
MODULE_NAME = 'libsovereign'


# Dynamically calculate the version based,
version = __import__(MODULE_NAME).get_version()


setup(
    name=MODULE_NAME,
    version=version,
    url='https://www.sousouindustries.com/',
    author='Cochise Ruhulessin',
    author_email='cochise.ruhulessin@sousouindustries.com',
    description=("A Python shared library for the Sovereign system."),
    license='Apache Licence 2.0',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
