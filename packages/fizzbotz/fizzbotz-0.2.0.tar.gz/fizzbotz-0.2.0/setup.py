#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('docs/history.rst') as history_file:
    history = history_file.read()

install_requires = [
    'aiohttp',
    'beautifulsoup4',
]

setup_requires = [
    'pytest-runner'
]

tests_require = [
    'pytest',
    'pytest-asyncio'
]

setup(
    name='fizzbotz',
    version='0.2.0',
    description='A bot for discord written in Python implementing some basic commands.',
    long_description=readme + '\n\n' + history,
    author='Matthew Martens',
    author_email='matthew.s.martens@gmail.com',
    url='https://github.com/martensm/fizzbotz',
    packages=[
        'fizzbotz',
    ],
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=setup_requires,
    license='MIT',
    zip_safe=False,
    keywords='fizzbotz',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=tests_require
)
