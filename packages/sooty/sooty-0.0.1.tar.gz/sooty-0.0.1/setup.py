# -*- coding: utf-8 -*-

from setuptools import setup

requires = ['docopt']

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sooty',
    version='0.0.1',
    description='Sooty: Simple database migrator.',
    long_description=readme,
    author='Jeff Zellman',
    author_email='jzellman@gmail.com',
    url='https://github.com/jzellman/sooty',
    license=license,
    py_modules=['sooty'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    entry_points = {
        'console_scripts': ['sooty=sooty:cli'],
    },
    install_requires=requires,
    zip_safe=False
)
