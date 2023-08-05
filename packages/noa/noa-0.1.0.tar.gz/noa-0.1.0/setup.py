# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

setup(
    name='noa',
    version='0.1.0',
    packages=find_packages(),
    package_data={'': ['*.yaml']},
    url='',
    license='MIT',
    author='Umut Karcı',
    author_email='cediddi@gmail.com',
    description='A simple regex finder',
    entry_points={
        'console_scripts': [
            'noa=noa:main',
        ]
    }
)
