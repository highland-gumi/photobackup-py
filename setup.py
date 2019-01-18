# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='photo-backup',
    version='0.1.0',
    description='photo backup tool for Python',
    long_description=readme,
    author='highland',
    author_email='',
    url='https://github.com/highland-gumi',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

