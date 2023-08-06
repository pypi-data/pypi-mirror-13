#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['requests==2.9.1'],

test_requirements = ['bumpversion==0.5.3',
                     'wheel==0.29.0',
                     'watchdog==0.8.3',
                     'flake8==2.4.1',
                     'tox==2.1.1',
                     'coverage==4.0',
                     'Sphinx==1.3.1'],

setup(
    name='iland-sdk',
    version='0.2.0',
    description="iland cloud Python SDK",
    long_description=readme + '\n\n' + history,
    author="iland Internet Solutions, Corp",
    author_email='devops@iland.com',
    url='https://github.com/ilanddev/python-sdk',
    packages=[
        '',
    ],
    package_dir={'':
                 'iland-sdk'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='iland cloud sdk',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
