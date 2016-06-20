#!/usr/bin/env python3

import re
import os.path
from setuptools import setup, find_packages
from pip.req import parse_requirements

here = os.path.abspath(os.path.dirname(__file__))

readme_path = os.path.join(here, 'README.md')
with open(readme_path, 'r') as readme_file:
    readme = readme_file.read()

# Borrowed from https://github.com/Gandi/gandi.cli/blob/master/setup.py
version_path = os.path.join(here, 'pianodb', '__init__.py')
with open(version_path, 'r') as version_file:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version_file.read()).group(1)

req_path = os.path.join(here, 'requirements.txt')
requirements = [str(r.req) for r in parse_requirements(req_path, session=False)]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pianodb',
    version=version,
    description="A database companion to pianobar.",
    long_description=readme,
    author="Reilly Tucker Siemens",
    author_email='reilly@tuckersiemens.com',
    url='https://github.com/reillysiemens/pianodb',
    packages=find_packages(),
    package_dir={'pianodb':
                 'pianodb'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='pianodb',
    py_modules=['pianodb'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'pianodb=pianodb.__main__:cli',
        ],
    },
)
